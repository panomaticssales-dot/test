import React, { useRef, useState } from 'react';
import './DragDropZone.css';

interface DragDropZoneProps {
  onImport: (files: FileList) => void;
  isProcessing: boolean;
}

const DragDropZone: React.FC<DragDropZoneProps> = ({ onImport, isProcessing }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onImport(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onImport(e.target.files);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="drag-drop-zone">
      <div
        className={`drop-area ${isDragging ? 'dragging' : ''} ${isProcessing ? 'disabled' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={!isProcessing ? handleClick : undefined}
      >
        <div className="drop-content">
          <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <h2>Drag & Drop Images Here</h2>
          <p>or click to browse</p>
          <div className="supported-formats">
            <span>CR2</span>
            <span>CR3</span>
            <span>JPG</span>
            <span>TIFF</span>
            <span>PNG</span>
          </div>
        </div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".cr2,.cr3,.jpg,.jpeg,.tiff,.tif,.png"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default DragDropZone;