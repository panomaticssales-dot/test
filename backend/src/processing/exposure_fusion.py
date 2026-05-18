"""
Exposure fusion using Mertens algorithm.
"""
import logging
from typing import List
import numpy as np
import cv2
from src.core.constants import (
    MERTENS_CONTRAST_WEIGHT,
    MERTENS_SATURATION_WEIGHT,
    MERTENS_EXPOSURE_WEIGHT,
    MAX_SCALE_PYRAMID,
)

logger = logging.getLogger("hdr_blender")


class ExposureFusion:
    """Mertens exposure fusion for natural HDR blending."""

    def __init__(
        self,
        contrast_weight: float = MERTENS_CONTRAST_WEIGHT,
        saturation_weight: float = MERTENS_SATURATION_WEIGHT,
        exposure_weight: float = MERTENS_EXPOSURE_WEIGHT,
    ):
        """Initialize exposure fusion parameters.

        Args:
            contrast_weight: Weight for contrast measure
            saturation_weight: Weight for saturation measure
            exposure_weight: Weight for exposure measure
        """
        self.contrast_weight = contrast_weight
        self.saturation_weight = saturation_weight
        self.exposure_weight = exposure_weight

    def fuse(self, images: List[np.ndarray]) -> np.ndarray:
        """Fuse multiple exposure images using Mertens algorithm.

        Args:
            images: List of aligned, normalized images [0, 1]

        Returns:
            Fused image as numpy array
        """
        if len(images) < 2:
            raise ValueError("At least 2 images required for fusion")

        logger.info(f"Fusing {len(images)} exposures using Mertens algorithm")

        # Compute weight maps
        weight_maps = []
        for i, img in enumerate(images):
            weights = self._compute_weight_map(img)
            weight_maps.append(weights)
            logger.debug(f"Computed weight map {i+1}/{len(images)}")

        # Normalize weight maps
        weight_sum = np.zeros_like(weight_maps[0])
        for w in weight_maps:
            weight_sum += w

        # Avoid division by zero
        weight_sum[weight_sum == 0] = 1.0

        # Multi-scale Laplacian pyramid blending
        fused = self._pyramid_blend(images, weight_maps, weight_sum)

        # Ensure output is in valid range
        fused = np.clip(fused, 0, 1)
        return fused

    def _compute_weight_map(self, image: np.ndarray) -> np.ndarray:
        """Compute weight map for single image.

        Combines three measures:
        1. Contrast (edge sharpness)
        2. Saturation (color intensity)
        3. Exposure (proximity to well-exposed)

        Args:
            image: Image array, normalized to [0, 1]

        Returns:
            Weight map same size as image
        """
        h, w = image.shape[:2]

        # Convert to grayscale and LAB for better perceptual measures
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32) / 255.0

        # 1. Contrast measure (Laplacian)
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        contrast = np.abs(laplacian)

        # 2. Saturation measure (color intensity in a,b channels)
        saturation = np.sqrt(lab[:, :, 1] ** 2 + lab[:, :, 2] ** 2)

        # 3. Exposure measure (distance from 0.5)
        exposure = np.exp(-((gray - 0.5) ** 2) / 0.08)

        # Combine measures
        weight = (
            (contrast ** self.contrast_weight)
            * (saturation ** self.saturation_weight)
            * (exposure ** self.exposure_weight)
        )

        return weight

    def _pyramid_blend(
        self, images: List[np.ndarray], weight_maps: List[np.ndarray], weight_sum: np.ndarray
    ) -> np.ndarray:
        """Blend images using Laplacian pyramid.

        Args:
            images: List of images to blend
            weight_maps: Weight map for each image
            weight_sum: Sum of all weight maps

        Returns:
            Blended image
        """
        # Build Laplacian pyramids for each image
        pyramids = []
        for img in images:
            pyr = self._build_laplacian_pyramid(img)
            pyramids.append(pyr)

        # Build weight pyramids
        weight_pyramids = []
        for wmap in weight_maps:
            wpyr = self._build_gaussian_pyramid(wmap)
            weight_pyramids.append(wpyr)

        # Blend pyramids level by level
        blended_pyramid = []
        for level in range(len(pyramids[0])):
            blended_level = np.zeros_like(pyramids[0][level])

            for img_idx in range(len(images)):
                # Resize weight to match level
                w = weight_pyramids[img_idx][level]
                # Ensure same spatial dimensions
                if w.shape[:2] != pyramids[img_idx][level].shape[:2]:
                    w = cv2.resize(w, (pyramids[img_idx][level].shape[1], pyramids[img_idx][level].shape[0]))

                # Weighted sum
                if len(pyramids[img_idx][level].shape) == 3:
                    blended_level += pyramids[img_idx][level] * w[:, :, np.newaxis]
                else:
                    blended_level += pyramids[img_idx][level] * w

            blended_pyramid.append(blended_level)

        # Reconstruct from pyramid
        result = self._reconstruct_from_pyramid(blended_pyramid)
        return result

    def _build_gaussian_pyramid(self, image: np.ndarray, levels: int = MAX_SCALE_PYRAMID) -> List[np.ndarray]:
        """Build Gaussian pyramid.

        Args:
            image: Input image
            levels: Number of pyramid levels

        Returns:
            List of pyramid levels
        """
        pyramid = [image]
        current = image
        for _ in range(levels - 1):
            current = cv2.pyrDown(current)
            pyramid.append(current)
        return pyramid

    def _build_laplacian_pyramid(
        self, image: np.ndarray, levels: int = MAX_SCALE_PYRAMID
    ) -> List[np.ndarray]:
        """Build Laplacian pyramid.

        Args:
            image: Input image
            levels: Number of pyramid levels

        Returns:
            List of Laplacian pyramid levels
        """
        gaussian_pyr = self._build_gaussian_pyramid(image, levels)
        laplacian_pyr = []

        for i in range(len(gaussian_pyr) - 1):
            # Expand next level
            expanded = cv2.pyrUp(gaussian_pyr[i + 1], dstsize=(gaussian_pyr[i].shape[1], gaussian_pyr[i].shape[0]))
            # Subtract
            laplacian = gaussian_pyr[i] - expanded
            laplacian_pyr.append(laplacian)

        # Add the last Gaussian level
        laplacian_pyr.append(gaussian_pyr[-1])
        return laplacian_pyr

    def _reconstruct_from_pyramid(self, pyramid: List[np.ndarray]) -> np.ndarray:
        """Reconstruct image from Laplacian pyramid.

        Args:
            pyramid: Laplacian pyramid levels

        Returns:
            Reconstructed image
        """
        result = pyramid[-1]
        for i in range(len(pyramid) - 2, -1, -1):
            expanded = cv2.pyrUp(result, dstsize=(pyramid[i].shape[1], pyramid[i].shape[0]))
            result = expanded + pyramid[i]
        return result
