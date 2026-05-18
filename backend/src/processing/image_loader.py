"""
Image loading utilities for RAW, JPEG, and TIFF formats.
"""
import logging
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import rawpy
import imageio

logger = logging.getLogger("hdr_blender")


class ImageLoader:
    """Load images from various formats (RAW, JPEG, TIFF, PNG)."""

    SUPPORTED_RAW_EXTENSIONS = {".cr2", ".cr3", ".nef", ".arw", ".raf"}
    SUPPORTED_RASTER_EXTENSIONS = {".jpg", ".jpeg", ".tiff", ".tif", ".png"}

    @staticmethod
    def load_image(image_path: str, normalize: bool = True) -> np.ndarray:
        """Load image from file.

        Args:
            image_path: Path to image file
            normalize: If True, normalize pixel values to [0, 1]

        Returns:
            Image as numpy array (BGR format for compatibility with OpenCV)
        """
        path = Path(image_path)
        suffix = path.suffix.lower()

        if suffix in ImageLoader.SUPPORTED_RAW_EXTENSIONS:
            return ImageLoader._load_raw(image_path, normalize)
        elif suffix in ImageLoader.SUPPORTED_RASTER_EXTENSIONS:
            return ImageLoader._load_raster(image_path, normalize)
        else:
            raise ValueError(f"Unsupported image format: {suffix}")

    @staticmethod
    def _load_raw(image_path: str, normalize: bool = True) -> np.ndarray:
        """Load RAW image using rawpy.

        Args:
            image_path: Path to RAW file
            normalize: If True, normalize to [0, 1]

        Returns:
            Image as numpy array
        """
        logger.debug(f"Loading RAW image: {image_path}")
        try:
            with rawpy.imread(image_path) as raw:
                # Postprocess RAW data
                rgb = raw.postprocess(
                    output_color=rawpy.colorspace.sRGB,
                    output_bps=16,  # 16-bit output for maximum quality
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,
                )
            # Convert RGB to BGR for OpenCV compatibility
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            if normalize:
                bgr = bgr.astype(np.float32) / 65535.0
            return bgr
        except Exception as e:
            logger.error(f"Failed to load RAW image {image_path}: {e}")
            raise

    @staticmethod
    def _load_raster(image_path: str, normalize: bool = True) -> np.ndarray:
        """Load raster image (JPEG, TIFF, PNG) using PIL/OpenCV.

        Args:
            image_path: Path to raster file
            normalize: If True, normalize to [0, 1]

        Returns:
            Image as numpy array
        """
        logger.debug(f"Loading raster image: {image_path}")
        try:
            # Try PIL first for TIFF (better metadata handling)
            pil_image = Image.open(image_path)
            image_array = np.array(pil_image)
            
            # Ensure BGR format
            if len(image_array.shape) == 3:
                if image_array.shape[2] == 3:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                elif image_array.shape[2] == 4:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
            
            image_array = image_array.astype(np.float32)
            if normalize:
                # Normalize based on dtype
                if image_array.max() > 1:
                    if image_array.max() > 255:
                        image_array = image_array / 65535.0  # 16-bit
                    else:
                        image_array = image_array / 255.0  # 8-bit
            
            return image_array
        except Exception as e:
            logger.error(f"Failed to load raster image {image_path}: {e}")
            raise

    @staticmethod
    def load_image_for_processing(image_path: str) -> Tuple[np.ndarray, dict]:
        """Load image and its metadata.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (image_array, metadata_dict)
        """
        try:
            image = ImageLoader.load_image(image_path, normalize=True)
            # Extract basic info
            metadata = {
                "shape": image.shape,
                "dtype": str(image.dtype),
                "min": float(image.min()),
                "max": float(image.max()),
            }
            return image, metadata
        except Exception as e:
            logger.error(f"Failed to load image for processing: {e}")
            raise
