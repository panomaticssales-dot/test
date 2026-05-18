"""
File and format validation utilities.
"""
import logging
from pathlib import Path
from src.core.config import Config

logger = logging.getLogger("hdr_blender")


def validate_image_file(file_path: str) -> bool:
    """Validate if file is a supported image format.

    Args:
        file_path: Path to file

    Returns:
        True if file is supported, False otherwise
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {file_path}")
        return False

    if not path.is_file():
        logger.warning(f"Path is not a file: {file_path}")
        return False

    if path.suffix.lower() not in Config.get_supported_extensions():
        logger.warning(f"Unsupported file format: {path.suffix}")
        return False

    return True


def validate_folder(folder_path: str) -> bool:
    """Validate if folder exists and is readable.

    Args:
        folder_path: Path to folder

    Returns:
        True if folder is valid, False otherwise
    """
    path = Path(folder_path)
    if not path.exists():
        logger.error(f"Folder not found: {folder_path}")
        return False

    if not path.is_dir():
        logger.error(f"Path is not a directory: {folder_path}")
        return False

    return True
