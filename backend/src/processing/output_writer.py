"""
Output writer for TIFF and other formats.
"""
import logging
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image
import tifffile
from src.models.image_models import ProcessingSettings
from src.core.constants import ANGLE_OUTPUT_FORMAT

logger = logging.getLogger("hdr_blender")


class OutputWriter:
    """Write processed images to output formats."""

    def __init__(self, settings: ProcessingSettings):
        """Initialize output writer.

        Args:
            settings: Output configuration
        """
        self.settings = settings

    def write_tiff(
        self, image: np.ndarray, output_path: str, angle_number: int
    ) -> str:
        """Write image as 16-bit TIFF file.

        Args:
            image: Image array, normalized to [0, 1]
            output_path: Directory to save file
            angle_number: Angle/sequence number for naming

        Returns:
            Path to written file
        """
        # Ensure output directory exists
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = ANGLE_OUTPUT_FORMAT.format(angle_number, self.settings.output_format)
        output_file = output_dir / filename

        # Convert to target bit depth
        if self.settings.output_bit_depth == 16:
            # Convert to 16-bit
            image_16bit = (np.clip(image, 0, 1) * 65535).astype(np.uint16)
            logger.debug(f"Converting to 16-bit: range [{image_16bit.min()}, {image_16bit.max()}]")
        elif self.settings.output_bit_depth == 32:
            # Keep as 32-bit float
            image_16bit = image.astype(np.float32)
            logger.debug(f"Keeping as 32-bit float: range [{image_16bit.min():.4f}, {image_16bit.max():.4f}]")
        else:
            raise ValueError(f"Unsupported bit depth: {self.settings.output_bit_depth}")

        # Write TIFF
        try:
            with tifffile.TiffWriter(str(output_file)) as tif:
                tif.write(
                    image_16bit,
                    photometric="rgb" if image_16bit.shape[2] == 3 else None,
                    compression=self.settings.output_compression,
                    metadata={
                        "angle": angle_number,
                        "processing": "HDR Exposure Fusion (Mertens)",
                    },
                )
            logger.info(f"Wrote TIFF: {output_file} ({output_file.stat().st_size / 1024 / 1024:.2f} MB)")
            return str(output_file)
        except Exception as e:
            logger.error(f"Failed to write TIFF {output_file}: {e}")
            raise
