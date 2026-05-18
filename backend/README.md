# HDR Blender Backend - Python

Professional exposure fusion processing engine for bracketed RAW and JPEG images.

## Tech Stack

- **Language**: Python 3.8+
- **Image Processing**: OpenCV, rawpy, LibRaw
- **HDR/Exposure Fusion**: OpenCV (Mertens algorithm)
- **RAW Support**: rawpy, imageio
- **Metadata**: piexif, PIL, rawpy
- **Alignment**: OpenCV ORB + Optical Flow
- **IPC**: FastAPI (Tauri bridge)

## Core Features

### 1. **Bracket Detection & Grouping**
- Analyzes EXIF metadata (exposure time, ISO, aperture)
- Groups images by scene/angle using:
  - Capture time proximity
  - Exposure values (EV)
  - Filename sequence patterns
  - Lens focal length
  - Camera model

### 2. **Image Alignment**
- ORB feature detection and matching
- Automatic homography calculation
- Perspective correction
- Robust to slight camera movement

### 3. **Exposure Fusion (Mertens Algorithm)**
- Well-exposedness measure
- Contrast measure
- Saturation measure
- Multi-scale Laplacian blending
- Natural appearance (no tone mapping artifacts)

### 4. **RAW Support**
- Canon CR2, CR3 (via rawpy + LibRaw)
- JPEG/JPG
- TIFF/TIF
- PNG (optional)

### 5. **Output**
- 16-bit TIFF export
- Automatic naming (angle_001.tiff, angle_002.tiff, etc.)
- Folder structure support

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                      # FastAPI entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── image_models.py          # Data models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration
│   │   ├── logging.py               # Logging setup
│   │   └── constants.py             # Constants
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── bracket_detector.py      # Bracket grouping
│   │   ├── image_loader.py          # Load RAW/JPEG/TIFF
│   │   ├── image_alignment.py       # Alignment pipeline
│   │   ├── exposure_fusion.py       # Mertens algorithm
│   │   ├── hdr_processor.py         # Main processor
│   │   └── output_writer.py         # TIFF export
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # API endpoints
│   │   └── schemas.py               # Request/response schemas
│   └── utils/
│       ├── __init__.py
│       ├── metadata.py              # EXIF parsing
│       ├── validation.py            # File validation
│       └── helpers.py               # Utility functions
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project metadata
├── Dockerfile                       # Docker configuration
└── README.md                        # Documentation
```

## Installation

### Prerequisites
- Python 3.8+
- LibRaw (system library)
- OpenCV (compiled with RAW support recommended)

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start backend server
python -m src.main
```

Backend runs on `http://localhost:8000`

## API Endpoints

### 1. Analyze Images
```
POST /api/analyze
Body: { "folder_path": "/path/to/images" }
Response: { "groups": [...], "total_images": 42 }
```

### 2. Process Brackets
```
POST /api/process
Body: {
  "bracket_groups": [...],
  "output_path": "/output",
  "settings": {...}
}
Response: { "status": "processing", "job_id": "uuid" }
```

### 3. Get Processing Status
```
GET /api/status/{job_id}
Response: { "progress": 45, "step": "aligning", "logs": [...] }
```

### 4. Get Processing Logs
```
WS /ws/logs/{job_id}
WebSocket stream of real-time logs
```

## Key Algorithms

### Bracket Detection
1. Read EXIF metadata from all images
2. Calculate EV (exposure value) from ISO, aperture, shutter speed
3. Sort by capture time
4. Group images with:
   - Time proximity < 1 second
   - Same focal length
   - EV differences in expected range (±2 stops)
   - Sequential filenames

### Image Alignment
1. Convert to grayscale
2. Detect ORB keypoints
3. Match features between reference and other exposures
4. Calculate homography matrix
5. Apply perspective transform

### Exposure Fusion (Mertens)
1. Normalize exposures to [0, 1]
2. Calculate:
   - Well-exposedness (Gaussian around middle gray)
   - Contrast (Laplacian magnitude)
   - Saturation (color intensity)
3. Weight maps combined with tuning parameters
4. Multi-scale Laplacian pyramid blending
5. Reconstruct from Laplacian pyramid

### Output
- Scale to 16-bit range (0-65535)
- Apply gamma correction
- Export as TIFF with metadata

## Configuration

Edit `src/core/config.py`:

```python
class Config:
    # Processing
    ALIGNMENT_METHOD = "ORB"  # or "SIFT", "AKAZE"
    FUSION_METHOD = "MERTENS"  # Exposure fusion algorithm
    
    # Bracket Detection
    TIME_PROXIMITY_SECONDS = 1.0
    EV_TOLERANCE = 0.3
    
    # Output
    OUTPUT_BIT_DEPTH = 16
    OUTPUT_FORMAT = "TIFF"
    
    # Advanced
    GPU_ENABLED = True
    DENOISE_STRENGTH = 0.5
    GHOST_REMOVAL = True
```

## Usage Example

```python
from src.processing.hdr_processor import HDRProcessor
from src.processing.bracket_detector import BracketDetector

# Detect brackets
detector = BracketDetector("/path/to/images")
groups = detector.detect_groups()

# Process
processor = HDRProcessor()
for group in groups:
    output = processor.process_bracket_group(
        images=group["images"],
        output_path="/output",
        angle_number=group["angle"]
    )
    print(f"Saved: {output}")
```

## Performance

- **Bracket Detection**: ~100ms for 1000 images
- **Image Loading (CR2)**: ~500ms per image
- **Alignment**: ~2-3 seconds per 3-bracket group
- **Fusion**: ~1-2 seconds per 3-bracket group
- **Export**: ~500ms per image

**Total for 3-bracket group**: ~5-7 seconds

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Docker

```bash
# Build image
docker build -t hdr-blender-backend .

# Run container
docker run -p 8000:8000 hdr-blender-backend
```

## Troubleshooting

### CR3 Files Not Loading
- Ensure LibRaw is installed: `brew install libraw` (macOS)
- Verify rawpy version: `pip install --upgrade rawpy`

### Slow Processing
- Enable GPU: Set `GPU_ENABLED=True`
- Reduce image resolution for testing
- Use faster alignment: `ALIGNMENT_METHOD="ORB"`

### Memory Issues
- Process images in batches
- Reduce image resolution
- Disable advanced features (denoise, ghost removal)

## Dependencies

See `requirements.txt` for complete list:
- opencv-python
- opencv-contrib-python
- rawpy
- Pillow
- numpy
- imageio
- piexif
- FastAPI
- uvicorn
- pydantic

## Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8
- All tests pass
- New features have tests
- Documentation is updated

## License

Proprietary - Panomatic Sales

## Support

For issues and feature requests, contact the development team.
