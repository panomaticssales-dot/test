"""
Image alignment for exposure brackets using feature matching.
"""
import logging
from typing import List, Optional, Tuple
import numpy as np
import cv2
from src.core.constants import MIN_FEATURE_MATCHES, DEFAULT_QUALITY_LEVEL, DEFAULT_NMS_THRESHOLD

logger = logging.getLogger("hdr_blender")


class ImageAligner:
    """Align multiple exposure images for bracket fusion."""

    def __init__(self, method: str = "ORB"):
        """Initialize aligner with feature detection method.

        Args:
            method: Feature detection method (ORB, SIFT, AKAZE)
        """
        self.method = method.upper()
        self.detector = self._create_detector()

    def _create_detector(self) -> cv2.Feature2D:
        """Create feature detector based on method.

        Returns:
            Feature detector object
        """
        if self.method == "ORB":
            return cv2.ORB_create(
                nfeatures=5000,
                scaleFactor=1.2,
                nlevels=8,
                edgeThreshold=15,
                fastThreshold=20,
                patchSize=31,
                wta_k=2,
                scoreType=cv2.ORB_HARRIS_SCORE,
            )
        elif self.method == "SIFT":
            return cv2.SIFT_create(
                nfeatures=5000,
                nOctaveLayers=3,
                contrastThreshold=0.03,
                edgeThreshold=10,
                sigma=1.6,
            )
        elif self.method == "AKAZE":
            return cv2.AKAZE_create(
                descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,
                descriptor_size=256,
                descriptor_channels=3,
                threshold=0.001,
                nOctaves=4,
                nOctaveLayers=4,
                diffusivity=cv2.KAZE_DIFF_PM_G2,
            )
        else:
            raise ValueError(f"Unknown detection method: {self.method}")

    def align_images(self, reference: np.ndarray, images: List[np.ndarray]) -> List[np.ndarray]:
        """Align multiple images to reference image.

        Args:
            reference: Reference image (usually middle exposure)
            images: List of images to align

        Returns:
            List of aligned images
        """
        logger.info(f"Aligning {len(images)} images using {self.method}")
        aligned = [reference]

        # Detect keypoints and descriptors in reference
        ref_gray = cv2.cvtColor((reference * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
        ref_kp, ref_desc = self.detector.detectAndCompute(ref_gray, None)

        if ref_desc is None or len(ref_kp) < MIN_FEATURE_MATCHES:
            logger.warning(f"Insufficient features detected in reference (found {len(ref_kp)})")
            return images

        # Create matcher
        if self.method == "ORB":
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        else:
            matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

        # Align each image
        for i, image in enumerate(images):
            try:
                img_gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
                img_kp, img_desc = self.detector.detectAndCompute(img_gray, None)

                if img_desc is None or len(img_kp) < MIN_FEATURE_MATCHES:
                    logger.warning(f"Image {i}: Insufficient features ({len(img_kp)})")
                    aligned.append(image)
                    continue

                # Match features
                matches = matcher.knnMatch(ref_desc, img_desc, k=2)

                # Apply Lowe's ratio test
                good_matches = []
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < 0.75 * n.distance:
                            good_matches.append(m)

                if len(good_matches) < MIN_FEATURE_MATCHES:
                    logger.warning(f"Image {i}: Too few good matches ({len(good_matches)})")
                    aligned.append(image)
                    continue

                # Calculate homography
                src_pts = np.float32([ref_kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([img_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                h_matrix, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

                if h_matrix is None:
                    logger.warning(f"Image {i}: Failed to compute homography")
                    aligned.append(image)
                    continue

                # Apply perspective transform
                h, w = reference.shape[:2]
                aligned_img = cv2.warpPerspective(image, h_matrix, (w, h))
                aligned.append(aligned_img)
                logger.debug(f"Image {i}: Aligned using {len(good_matches)} matches")
            except Exception as e:
                logger.error(f"Image {i}: Alignment failed: {e}")
                aligned.append(image)

        return aligned
