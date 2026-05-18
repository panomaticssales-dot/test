"""
Data models for image processing requests/responses.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class AlignmentMethod(str, Enum):
    """Image alignment methods."""
    ORB = "orb"
    SIFT = "sift"
    AKAZE = "akaze"


class FusionMethod(str, Enum):
    """Exposure fusion methods."""
    MERTENS = "mertens"
    TONE_MAPPING = "tone_mapping"


@dataclass
class ProcessingSettings:
    """Settings for HDR processing."""
    alignment_method: AlignmentMethod = AlignmentMethod.ORB
    fusion_method: FusionMethod = FusionMethod.MERTENS
    output_bit_depth: int = 16
    output_format: str = "tiff"
    enable_denoise: bool = False
    enable_ghost_removal: bool = False
    enable_lens_correction: bool = False
    enable_chromatic_correction: bool = False


@dataclass
class ImageFile:
    """Represents an image file."""
    path: str
    filename: str
    format: str
    size_bytes: int
    exif_data: Optional[Dict[str, Any]] = None


@dataclass
class BracketGroup:
    """Group of bracketed exposures."""
    angle_number: int
    images: List[ImageFile] = field(default_factory=list)
    exposure_values: List[float] = field(default_factory=list)
    capture_time: Optional[str] = None
    focal_length: Optional[float] = None

    def __post_init__(self):
        """Validate bracket group."""
        if len(self.images) < 2:
            raise ValueError("Bracket group must have at least 2 images")


@dataclass
class ProcessingJob:
    """Represents a processing job."""
    job_id: str
    status: str = "queued"  # queued, processing, complete, error
    progress: int = 0
    current_step: str = ""
    logs: List[str] = field(default_factory=list)
    bracket_groups: List[BracketGroup] = field(default_factory=list)
    output_path: str = ""
    settings: ProcessingSettings = field(default_factory=ProcessingSettings)
    error_message: Optional[str] = None
