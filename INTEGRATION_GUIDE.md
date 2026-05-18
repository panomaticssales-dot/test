# Frontend-Backend Integration Guide

## Overview

The HDR Blender application uses a **Tauri IPC bridge** to communicate between the React frontend and Python backend.

```
┌─────────────────────────────────────────────────────────────┐
│                    React + Tauri Frontend                   │
│                    (TypeScript/React)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │   Tauri IPC Bridge  │
                │   (Rust Commands)   │
                └──────────┬──────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 Python Backend (FastAPI)                    │
│              src/main.py (uvicorn server)                   │
└──────────────────────────────────────────────────────────────┘
                           ▲
                           │
                ┌──────────▼──────────┐
                │  Processing Pipeline │
                │  - Bracket Detection │
                │  - Image Alignment   │
                │  - Exposure Fusion   │
                │  - TIFF Output       │
                └─────────────────────┘
```

## Architecture

### Tauri IPC Commands

The Tauri Rust backend (`src-tauri/src/main.rs`) exposes these commands:

1. **start_backend()** - Start Python backend process
2. **check_backend_health()** - Verify backend is running
3. **analyze_images(folder_path)** - Detect bracket groups
4. **process_images(request)** - Start HDR processing
5. **get_job_status(job_id)** - Poll processing status
6. **stop_backend()** - Kill backend process

### React Hooks

**useBackend()** hook (`src/hooks/useBackend.ts`):

```typescript
const {
  backendHealthy,      // Is backend running?
  isInitializing,      // Startup in progress?
  isAnalyzing,         // Analysis in progress?
  isProcessing,        // Processing in progress?
  analysisResult,      // Bracket detection results
  processingJobId,     // Current job ID
  jobStatus,           // Processing status & logs
  error,               // Error message
  // Methods...
  analyzeImages,
  startProcessing,
  pollJobStatus,
} = useBackend();
```

### Workflow

```
1. App Starts
   ↓
2. useBackend() initializes Tauri
   ↓
3. start_backend() spawns Python process
   ↓
4. Backend listens on http://localhost:8000
   ↓
5. User imports images via drag-drop
   ↓
6. analyzeImages() calls /api/analyze
   ↓
7. Bracket groups displayed in UI
   ↓
8. User configures settings
   ↓
9. startProcessing() calls /api/process
   ↓
10. pollJobStatus() polls /api/status/{job_id}
    ↓
11. Real-time logs streamed to UI
    ↓
12. Output files saved to disk
```

## File Structure

### Frontend Files

```
src/
├── utils/
│   └── backend.ts              # Backend API client
├── hooks/
│   └── useBackend.ts           # React hook for backend integration
├── components/
│   ├── BackendStatus.tsx       # Status indicator
│   ├── BackendStatus.css
│   ├── ProcessingStatus.tsx    # Real-time status display
│   ├── ProcessingStatus.css
│   ├── DragDropZone.tsx        # File import
│   ├── ImageGrouping.tsx       # Bracket preview
│   └── ExportSettings.tsx      # Output configuration
└── App.tsx                     # Main app with integration
```

### Rust Tauri Files

```
src-tauri/
├── src/
│   └── main.rs                 # IPC command handlers
├── Cargo.toml                  # Rust dependencies
├── tauri.conf.json             # Tauri configuration
└── build.rs                    # Build script
```

## API Flow Examples

### 1. Analyze Images

```typescript
// Frontend
const result = await BackendClient.analyzeImages("/path/to/images");

// Tauri
invoke("analyze_images", { folderPath })

// Rust
BackendClient::analyzeImages(folder_path)
  → HTTP POST /api/analyze?folder_path=...

// Python
GET /api/analyze
  → BracketDetector.detect_groups()
  → Return BracketGroupInfo[]
```

### 2. Process Images

```typescript
// Frontend
const response = await BackendClient.processImages({
  folder_path: "/images",
  output_path: "/output",
  enable_denoise: true,
  enable_ghost_removal: false,
  enable_lens_correction: false,
  enable_chromatic_correction: false,
});

const jobId = response.job_id;

// Tauri
invoke("process_images", { request })
  → HTTP POST /api/process?...

// Python
POST /api/process
  → Create ProcessingJob
  → Start async background task
  → Return job_id
```

### 3. Poll Job Status

```typescript
// Frontend (runs every 1 second)
const status = await BackendClient.getJobStatus(jobId);

// Tauri
invoke("get_job_status", { jobId })
  → HTTP GET /api/status/{job_id}

// Python
GET /api/status/{job_id}
  → Get ProcessingJob from memory
  → Return JobStatus {
      status: "processing",
      progress: 45,
      logs: [...],
      error_message: null,
      output_files: null
    }
```

## Installation & Setup

### Prerequisites

- Node.js 16+
- Python 3.8+
- Rust 1.57+
- Tauri CLI

### Setup Steps

```bash
# 1. Install frontend dependencies
npm install

# 2. Install Tauri CLI
npm install -D @tauri-apps/cli

# 3. Install Python backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 4. Run in development mode
npm run tauri dev

# 5. Build for production
npm run tauri build
```

## Development

### Frontend Development

```bash
# Run frontend dev server (without Tauri)
npm run dev

# Run with Tauri (includes backend)
npm run tauri dev
```

### Backend Development

```bash
# Run backend directly (outside Tauri)
cd backend
python -m src.main

# Backend runs on http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Testing the Integration

```typescript
// Test in browser console
import { BackendClient } from "./utils/backend";

// Start backend
await BackendClient.startBackend();

// Check health
const healthy = await BackendClient.checkHealth();
console.log("Backend healthy:", healthy);

// Analyze images
const result = await BackendClient.analyzeImages("/path/to/images");
console.log("Analysis:", result);

// Process images
const response = await BackendClient.processImages({
  folder_path: "/images",
  output_path: "/output",
  enable_denoise: false,
  enable_ghost_removal: false,
  enable_lens_correction: false,
  enable_chromatic_correction: false,
});

// Poll status
const status = await BackendClient.getJobStatus(response.job_id);
console.log("Status:", status);
```

## Configuration

### Backend Configuration

Edit `backend/src/core/config.py`:

```python
class Config:
    API_HOST = "127.0.0.1"
    API_PORT = 8000
    ALIGNMENT_METHOD = "ORB"
    FUSION_METHOD = "MERTENS"
    OUTPUT_BIT_DEPTH = 16
    # ... more settings
```

### Tauri Configuration

Edit `src-tauri/tauri.conf.json`:

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  // ... more config
}
```

## Error Handling

### Backend Not Starting

1. Check if port 8000 is available
2. Verify Python is installed and in PATH
3. Check backend logs in `backend/logs/hdr_blender.log`

### Analysis Fails

1. Verify folder path is valid
2. Check supported image formats (CR2, CR3, JPG, TIFF, PNG)
3. Ensure LibRaw is installed: `pip install --upgrade rawpy`

### Processing Timeout

1. Images are being processed in background
2. Check job status with `GET /api/status/{job_id}`
3. Verify disk space for output files

## Performance Tips

1. **GPU Acceleration**: Set `GPU_ENABLED=True` in config
2. **Batch Processing**: Process multiple bracket groups in parallel
3. **Memory Management**: Reduce image resolution for testing
4. **Alignment Speed**: Use ORB instead of SIFT/AKAZE

## Troubleshooting

### Issue: Backend process not found

```bash
# Manually start backend
cd backend
python -m src.main

# Then run Tauri separately
npm run tauri dev
```

### Issue: CORS errors

Tauri origins configured in `src-tauri/tauri.conf.json`:

```json
"allowlist": {
  "all": true,
  "fs": { "all": true },
  "shell": { "open": true }
}
```

### Issue: Image not loading

```bash
# Verify rawpy installation
pip install --upgrade rawpy

# Install system dependencies
# macOS
brew install libraw

# Ubuntu
sudo apt-get install libraw-dev

# Windows
# Download LibRaw binary
```

## Future Improvements

1. **WebSocket Logs** - Real-time log streaming instead of polling
2. **Job Persistence** - Save job state to database
3. **Batch Queue** - Queue multiple processing jobs
4. **GPU Support** - CUDA acceleration for faster processing
5. **Advanced Settings** - Fine-tune Mertens parameters in UI
