"""
FastAPI routes for HDR processing.
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import List
import asyncio
import uuid
from src.processing.bracket_detector import BracketDetector
from src.processing.hdr_processor import HDRProcessor
from src.models.image_models import ProcessingSettings
from src.utils.validation import validate_folder
from src.core.logging import logger

router = APIRouter(prefix="/api", tags=["processing"])

# In-memory job storage (use database in production)
jobs = {}


@router.post("/analyze")
async def analyze_images(folder_path: str):
    """Analyze folder and detect bracket groups.

    Args:
        folder_path: Path to folder containing images

    Returns:
        JSON with detected groups and image count
    """
    if not validate_folder(folder_path):
        raise HTTPException(status_code=400, detail="Invalid folder path")

    try:
        detector = BracketDetector(folder_path)
        groups = detector.detect_groups()

        return {
            "status": "success",
            "groups": [
                {
                    "angle": g.angle_number,
                    "images": len(g.images),
                    "exposures": g.exposure_values,
                    "filenames": [img.filename for img in g.images],
                }
                for g in groups
            ],
            "total_images": sum(len(g.images) for g in groups),
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_images(
    folder_path: str,
    output_path: str,
    enable_denoise: bool = False,
    enable_ghost_removal: bool = False,
    enable_lens_correction: bool = False,
    enable_chromatic_correction: bool = False,
):
    """Start processing images to HDR.

    Args:
        folder_path: Path to input folder
        output_path: Path to output folder
        enable_denoise: Enable denoising
        enable_ghost_removal: Enable ghost removal
        enable_lens_correction: Enable lens correction
        enable_chromatic_correction: Enable chromatic aberration correction

    Returns:
        JSON with job ID
    """
    if not validate_folder(folder_path):
        raise HTTPException(status_code=400, detail="Invalid input folder")

    if not validate_folder(output_path):
        raise HTTPException(status_code=400, detail="Invalid output folder")

    # Create job
    job_id = str(uuid.uuid4())
    settings = ProcessingSettings(
        enable_denoise=enable_denoise,
        enable_ghost_removal=enable_ghost_removal,
        enable_lens_correction=enable_lens_correction,
        enable_chromatic_correction=enable_chromatic_correction,
    )

    jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "logs": ["Starting processing..."],
    }

    # Process in background (in production, use task queue)
    asyncio.create_task(process_background(job_id, folder_path, output_path, settings))

    return {"status": "accepted", "job_id": job_id}


async def process_background(job_id: str, folder_path: str, output_path: str, settings: ProcessingSettings):
    """Background processing task."""
    try:
        processor = HDRProcessor(settings)
        output_files = processor.process_folder(folder_path, output_path)

        jobs[job_id] = {
            "status": "complete",
            "progress": 100,
            "logs": jobs[job_id]["logs"] + [f"Generated {len(output_files)} HDR images"],
            "output_files": output_files,
        }
    except Exception as e:
        logger.error(f"Background processing failed: {e}")
        jobs[job_id] = {
            "status": "error",
            "progress": 0,
            "logs": jobs[job_id]["logs"] + [f"Error: {str(e)}"],
            "error": str(e),
        }


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get processing job status.

    Args:
        job_id: Job ID

    Returns:
        JSON with job status
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return jobs[job_id]
