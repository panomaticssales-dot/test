# HDR Blender - Frontend (Tauri + React + TypeScript)

Professional desktop application for photographers to blend bracketed exposures into HDR TIFFs.

## Tech Stack

- **Framework**: Tauri (Rust backend with web frontend)
- **UI Library**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS3 with modern gradients and animations

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── DragDropZone.tsx         # Image import interface
│   │   ├── ImageGrouping.tsx        # Bracket grouping preview
│   │   ├── ProcessingStatus.tsx     # Progress tracking
│   │   └── ExportSettings.tsx       # Export configuration
│   ├── App.tsx                      # Main app component
│   ├── App.css                      # Global styles
│   ├── index.css                    # CSS reset
│   └── main.tsx                     # React entry point
├── src-tauri/
│   ├── src/
│   │   └── main.rs                  # Tauri backend entry
│   ├── Cargo.toml                   # Rust dependencies
│   └── tauri.conf.json              # Tauri configuration
├── index.html                       # HTML root
├── package.json                     # Node dependencies
├── vite.config.ts                   # Vite configuration
├── tsconfig.json                    # TypeScript config
└── README.md                        # This file
```

## Features

### 1. **Drag & Drop Import**
- Users can drag folders or individual image files
- Supports CR2, CR3, JPG, TIFF, PNG formats
- Real-time file validation

### 2. **Auto Image Grouping**
- Analyzes metadata to detect exposure brackets
- Groups images by angle/scene automatically
- Preview grouping results before processing

### 3. **Processing Monitor**
- Real-time progress bar
- Detailed processing logs
- Step-by-step status updates

### 4. **Export Configuration**
- Choose output directory
- Configure file format (TIFF/TIF)
- Select bit depth (16-bit or 32-bit)
- Toggle optional features (denoise, ghost removal, lens correction)

## Installation & Setup

### Prerequisites

- Node.js 16+ (for frontend)
- Rust 1.56+ (for Tauri)
- npm or yarn

### Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run tauri-dev

# Build for production
npm run tauri-build
```

## Scripts

- `npm run dev` - Start Vite dev server
- `npm run build` - Build React app
- `npm run tauri` - Tauri CLI commands
- `npm run tauri-dev` - Run Tauri development
- `npm run tauri-build` - Build Tauri application

## UI Workflow

```
1. Import Images
   ↓
   [Drag & Drop Zone]
   ↓
2. Analyze Brackets
   ↓
   [Image Grouping Preview]
   ↓
3. Configure Export
   ↓
   [Export Settings]
   ↓
4. Process Images
   ↓
   [Processing Status Monitor]
   ↓
5. Complete
   ↓
   [Export Results]
```

## Component Details

### DragDropZone
- Main entry point for image import
- Drag/drop or file browser
- Format compatibility display

### ImageGrouping
- Simulates backend grouping analysis
- Shows detected angle groups
- Allows export path selection

### ProcessingStatus
- Displays real-time progress
- Shows 4-step processing pipeline
- Logs detailed messages

### ExportSettings
- Output directory selection
- Format and quality options
- Advanced feature toggles

## Styling

Modern gradient design with:
- Deep purple/blue color scheme (#667eea, #764ba2)
- Glassmorphism effects with backdrop filters
- Smooth animations and transitions
- Responsive grid layouts

### Color Palette

- **Primary Gradient**: #667eea → #764ba2
- **Background**: #1e1e2e to #2a2a3e
- **Surface**: rgba(0, 0, 0, 0.3)
- **Text**: rgba(255, 255, 255, 0.87)

## Communication with Backend

All component interactions use Tauri's `invoke` API to communicate with the Rust backend:

```typescript
import { invoke } from '@tauri-apps/api/tauri'

// Example: Process images
const result = await invoke('process_images', {
  imagePaths: [...],
})
```

## Next Steps

1. **Backend Integration**: Connect frontend commands to Python backend via Tauri
2. **File Dialog Integration**: Implement native file/folder selection
3. **Real-time Logging**: Stream processing logs from backend
4. **Image Preview**: Display thumbnail previews in grouping view
5. **Keyboard Shortcuts**: Add hotkeys for common actions
6. **Dark/Light Theme**: Implement theme toggle

## Browser Support

- Chrome 104+
- Safari 15+
- Firefox 102+
- Electron-compatible browser APIs

## License

Proprietary - Panomatic Sales

## Support

For issues and feature requests, contact the development team.
