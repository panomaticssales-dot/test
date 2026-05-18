"""
Core configuration for HDR Blender backend.
"""
import os
from pathlib import Path


class Config:
    """Application configuration."""

    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TEMP_DIR = BASE_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"

    # Processing settings
    ALIGNMENT_METHOD = "ORB"  # ORB, SIFT, AKAZE
    FUSION_METHOD = "MERTENS"  # Exposure fusion algorithm
    GPU_ENABLED = False

    # Bracket detection
    TIME_PROXIMITY_SECONDS = 1.0
    EV_TOLERANCE = 0.3
    MIN_BRACKET_COUNT = 2
    MAX_BRACKET_COUNT = 11

    # Output settings
    OUTPUT_BIT_DEPTH = 16  # 16 or 32
    OUTPUT_FORMAT = "TIFF"
    OUTPUT_COMPRESSION = "lzw"

    # Advanced processing
    DENOISE_ENABLED = False
    DENOISE_STRENGTH = 0.5
    GHOST_REMOVAL_ENABLED = False
    LENS_CORRECTION_ENABLED = False
    CHROMATIC_ABERRATION_ENABLED = False

    # API settings
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_WORKERS = int(os.getenv("API_WORKERS", 4))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Supported file types
    SUPPORTED_FORMATS = {
        "raw": [".cr2", ".cr3", ".nef", ".arw", ".raf"],
        "jpeg": [".jpg", ".jpeg"],
        "tiff": [".tiff", ".tif"],
        "other": [".png"],
    }

    @classmethod
    def get_supported_extensions(cls) -> set:
        """Get all supported file extensions."""
        extensions = set()
        for format_list in cls.SUPPORTED_FORMATS.values():
            extensions.update(format_list)
        return extensions
