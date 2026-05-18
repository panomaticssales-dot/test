"""
Bracket detection algorithm for grouping exposure brackets.
"""
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import piexif
from src.utils.metadata import get_image_metadata
from src.models.image_models import ImageFile, BracketGroup
from src.core.config import Config

logger = logging.getLogger("hdr_blender")


class BracketDetector:
    """Detects and groups exposure brackets from a folder of images."""

    def __init__(self, folder_path: str):
        """Initialize bracket detector.

        Args:
            folder_path: Path to folder containing images
        """
        self.folder_path = Path(folder_path)
        self.images: List[ImageFile] = []
        self.supported_extensions = Config.get_supported_extensions()

    def scan_folder(self) -> List[ImageFile]:
        """Scan folder for supported image files.

        Returns:
            List of ImageFile objects
        """
        logger.info(f"Scanning folder: {self.folder_path}")
        images = []

        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")

        # Recursively find all supported image files
        for file_path in self.folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    exif_data = get_image_metadata(str(file_path))
                    image = ImageFile(
                        path=str(file_path),
                        filename=file_path.name,
                        format=file_path.suffix.lower(),
                        size_bytes=file_path.stat().st_size,
                        exif_data=exif_data,
                    )
                    images.append(image)
                    logger.debug(f"Loaded: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Failed to load {file_path.name}: {e}")

        self.images = sorted(images, key=lambda x: x.exif_data.get("datetime", "") if x.exif_data else "")
        logger.info(f"Found {len(self.images)} images")
        return self.images

    def calculate_exposure_value(self, image: ImageFile) -> Optional[float]:
        """Calculate exposure value (EV) from EXIF data.

        Formula: EV = log2(N²/t) + log2(100/ISO)
        where N = aperture, t = shutter speed, ISO = ISO sensitivity

        Args:
            image: ImageFile object

        Returns:
            Exposure value as float, or None if data unavailable
        """
        if not image.exif_data:
            return None

        try:
            iso = float(image.exif_data.get("iso", 100))
            aperture = float(image.exif_data.get("aperture", 1.4))
            shutter_speed = float(image.exif_data.get("shutter_speed", 1.0))

            # EV = log2(N²/t) + log2(100/ISO)
            import math
            ev = math.log2((aperture ** 2) / shutter_speed) + math.log2(100 / iso)
            return ev
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    def detect_groups(self) -> List[BracketGroup]:
        """Detect bracket groups from scanned images.

        Grouping algorithm:
        1. Sort images by capture time
        2. Group images with similar capture times (within TIME_PROXIMITY_SECONDS)
        3. Further group by focal length
        4. Verify EV values form valid bracket pattern

        Returns:
            List of BracketGroup objects
        """
        if not self.images:
            self.scan_folder()

        logger.info("Detecting bracket groups...")
        groups: List[BracketGroup] = []
        processed_indices = set()

        for i, image in enumerate(self.images):
            if i in processed_indices:
                continue

            # Start a new group
            current_group = [image]
            processed_indices.add(i)
            current_time = image.exif_data.get("datetime") if image.exif_data else None
            current_focal_length = image.exif_data.get("focal_length") if image.exif_data else None

            # Find matching exposures
            for j in range(i + 1, len(self.images)):
                if j in processed_indices:
                    continue

                candidate = self.images[j]
                candidate_time = candidate.exif_data.get("datetime") if candidate.exif_data else None
                candidate_focal_length = candidate.exif_data.get("focal_length") if candidate.exif_data else None

                # Check time proximity
                if current_time and candidate_time:
                    try:
                        time_diff = abs(
                            (datetime.fromisoformat(candidate_time) - datetime.fromisoformat(current_time)).total_seconds()
                        )
                        if time_diff > Config.TIME_PROXIMITY_SECONDS:
                            break
                    except (ValueError, TypeError):
                        pass

                # Check focal length match
                if current_focal_length and candidate_focal_length:
                    if abs(current_focal_length - candidate_focal_length) > 1.0:  # 1mm tolerance
                        continue

                current_group.append(candidate)
                processed_indices.add(j)

                if len(current_group) >= Config.MAX_BRACKET_COUNT:
                    break

            # Verify group has minimum images
            if len(current_group) >= Config.MIN_BRACKET_COUNT:
                bracket_group = BracketGroup(
                    angle_number=len(groups) + 1,
                    images=current_group,
                    exposure_values=[self.calculate_exposure_value(img) or 0.0 for img in current_group],
                    capture_time=current_time,
                    focal_length=current_focal_length,
                )
                groups.append(bracket_group)
                logger.info(
                    f"Detected angle {bracket_group.angle_number}: "
                    f"{len(current_group)} images, EV values: {bracket_group.exposure_values}"
                )

        logger.info(f"Detected {len(groups)} bracket groups")
        return groups
