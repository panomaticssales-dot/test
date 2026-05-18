"""
Main HDR processing pipeline orchestrator.
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from src.processing.bracket_detector import BracketDetector
from src.processing.image_loader import ImageLoader
from src.processing.image_alignment import ImageAligner
from src.processing.exposure_fusion import ExposureFusion
from src.processing.output_writer import OutputWriter
from src.models.image_models import BracketGroup, ProcessingSettings

logger = logging.getLogger("hdr_blender")


class HDRProcessor:
    """Main HDR processing pipeline."""

    def __init__(self, settings: Optional[ProcessingSettings] = None):
        """Initialize HDR processor.

        Args:
            settings: Processing configuration
        """
        self.settings = settings or ProcessingSettings()
        self.aligner = ImageAligner(method=self.settings.alignment_method.value)
        self.fusion = ExposureFusion()
        self.writer = OutputWriter(settings)

    def process_bracket_group(
        self, bracket_group: BracketGroup, output_path: str, angle_number: Optional[int] = None
    ) -> str:
        """Process a single bracket group to HDR image.

        Args:
            bracket_group: BracketGroup containing images to process
            output_path: Directory to save output
            angle_number: Override angle number for naming

        Returns:
            Path to output file
        """
        logger.info(f"Processing bracket group with {len(bracket_group.images)} images")

        # Load images
        images = []
        for image_file in bracket_group.images:
            try:
                img = ImageLoader.load_image(image_file.path, normalize=True)
                images.append(img)
                logger.debug(f"Loaded: {image_file.filename}")
            except Exception as e:
                logger.error(f"Failed to load {image_file.filename}: {e}")
                raise

        if len(images) < 2:
            raise ValueError("Bracket group must have at least 2 images")

        # Align images (use first as reference)
        logger.info("Aligning exposures...")
        reference = images[0]
        other_images = images[1:]
        aligned = [reference] + self.aligner.align_images(reference, other_images)

        # Fuse exposures
        logger.info("Fusing exposures...")
        fused = self.fusion.fuse(aligned)

        # Write output
        angle_num = angle_number or bracket_group.angle_number
        output_file = self.writer.write_tiff(
            image=fused, output_path=output_path, angle_number=angle_num
        )

        logger.info(f"Output saved: {output_file}")
        return output_file

    def process_folder(self, folder_path: str, output_path: str) -> List[str]:
        """Process all bracket groups in a folder.

        Args:
            folder_path: Folder containing images
            output_path: Directory to save outputs

        Returns:
            List of output file paths
        """
        logger.info(f"Processing folder: {folder_path}")

        # Detect brackets
        detector = BracketDetector(folder_path)
        groups = detector.detect_groups()

        if not groups:
            logger.warning("No bracket groups detected")
            return []

        # Process each group
        output_files = []
        for i, group in enumerate(groups, 1):
            try:
                output_file = self.process_bracket_group(group, output_path, angle_number=i)
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"Failed to process group {i}: {e}")

        logger.info(f"Processing complete. Generated {len(output_files)} HDR images")
        return output_files
