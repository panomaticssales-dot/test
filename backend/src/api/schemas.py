"""
Request/response schemas for API.
"""
from pydantic import BaseModel
from typing import List, Optional
from src.models.image_models import ProcessingSettings, BracketGroup


class AnalyzeRequest(BaseModel):
    """Request to analyze images."""
    folder_path: str


class AnalyzeResponse(BaseModel):
    """Response from image analysis."""
    status: str
    groups: List[dict]
    total_images: int


class ProcessRequest(BaseModel):
    """Request to process images."""
    folder_path: str
    output_path: str
    settings: Optional[ProcessingSettings] = None


class ProcessResponse(BaseModel):
    """Response from processing request."""
    status: str
    job_id: str


class JobStatus(BaseModel):
    """Processing job status."""
    job_id: str
    status: str
    progress: int
    logs: List[str]
    error_message: Optional[str] = None
