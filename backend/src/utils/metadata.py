"""
Metadata extraction from image files.
"""
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import piexif
from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger("hdr_blender")


def get_image_metadata(image_path: str) -> Optional[Dict[str, Any]]:
    """Extract metadata from image file.

    Args:
        image_path: Path to image file

    Returns:
        Dictionary with extracted metadata or None if unavailable
    """
    try:
        with Image.open(image_path) as img:
            metadata = {}
            
            # Try to get EXIF data
            try:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        metadata[tag_name.lower()] = value
            except (AttributeError, KeyError):
                pass

            # Extract specific fields
            result = {
                "filename": image_path.split("/")[-1],
                "datetime": metadata.get("datetime", ""),
                "iso": int(metadata.get("isospeedratings", 100)) if metadata.get("isospeedratings") else 100,
                "aperture": float(metadata.get("fnumber", [1.4])[0]) if isinstance(metadata.get("fnumber"), (list, tuple)) else 1.4,
                "shutter_speed": float(metadata.get("exposuretime", [1.0])[0]) if isinstance(metadata.get("exposuretime"), (list, tuple)) else 1.0,
                "focal_length": float(metadata.get("focallength", [50.0])[0]) if isinstance(metadata.get("focallength"), (list, tuple)) else 50.0,
                "camera_model": metadata.get("model", ""),
                "lens_model": metadata.get("lensmodel", ""),
            }
            return result
    except Exception as e:
        logger.debug(f"Failed to extract metadata from {image_path}: {e}")
        return None
