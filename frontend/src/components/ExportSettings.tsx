import React, { useState } from 'react';
import './ExportSettings.css';

interface ExportSettingsProps {
  onExport: (settings: ExportConfig) => void;
  onBack: () => void;
}

interface ExportConfig {
  outputPath: string;
  bitDepth: '16' | '32';
  format: 'tiff' | 'tif';
  enableDenoise: boolean;
  enableGhostRemoval: boolean;
  enableLensCorrection: boolean;
  enableChromaticCorrection: boolean;
}

const ExportSettings: React.FC<ExportSettingsProps> = ({ onExport, onBack }) => {
  const [settings, setSettings] = useState<ExportConfig>({
    outputPath: '',
    bitDepth: '16',
    format: 'tiff',
    enableDenoise: false,
    enableGhostRemoval: false,
    enableLensCorrection: false,
    enableChromaticCorrection: false,
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handlePathSelect = async () => {
    // In a real app, this would call the Tauri file dialog
    const defaultPath = '/output';
    setSettings({ ...settings, outputPath: defaultPath });
  };

  const handleToggle = (key: keyof ExportConfig) => {
    setSettings({
      ...settings,
      [key]: !settings[key],
    });
  };

  const handleSelectChange = (key: keyof ExportConfig, value: string) => {
    setSettings({
      ...settings,
      [key]: value,
    });
  };

  const isValid = settings.outputPath.length > 0;

  return (
    <div className="export-settings">
      <div className="settings-header">
        <h2>Export Settings</h2>
        <p>Configure how your HDR images will be saved</p>
      </div>

      <div className="settings-container">
        {/* Output Path */}
        <div className="setting-group">
          <label htmlFor="output-path" className="setting-label">
            Output Folder
          </label>
          <div className="path-input-group">
            <input
              id="output-path"
              type="text"
              value={settings.outputPath}
              readOnly
              placeholder="Select output folder..."
              className="path-input"
            />
            <button className="btn-browse" onClick={handlePathSelect}>
              Browse
            </button>
          </div>
        </div>

        {/* Output Format */}
        <div className="settings-row">
          <div className="setting-group">
            <label htmlFor="bit-depth" className="setting-label">
              Bit Depth
            </label>
            <select
              id="bit-depth"
              value={settings.bitDepth}
              onChange={(e) => handleSelectChange('bitDepth' as keyof ExportConfig, e.target.value)}
              className="setting-select"
            >
              <option value="16">16-bit (Standard)</option>
              <option value="32">32-bit (Maximum Quality)</option>
            </select>
          </div>

          <div className="setting-group">
            <label htmlFor="format" className="setting-label">
              Format
            </label>
            <select
              id="format"
              value={settings.format}
              onChange={(e) => handleSelectChange('format' as keyof ExportConfig, e.target.value)}
              className="setting-select"
            >
              <option value="tiff">TIFF</option>
              <option value="tif">TIF</option>
            </select>
          </div>
        </div>

        {/* Basic Options */}
        <div className="setting-group">
          <div className="setting-checkbox">
            <input
              id="ghost-removal"
              type="checkbox"
              checked={settings.enableGhostRemoval}
              onChange={() => handleToggle('enableGhostRemoval')}
            />
            <label htmlFor="ghost-removal" className="checkbox-label">
              Ghost Removal
              <span className="help-text">Remove moving objects from different exposures</span>
            </label>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="advanced-section">
          <button
            className="advanced-toggle"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            <span className="toggle-icon">{showAdvanced ? '▼' : '▶'}</span>
            Advanced Options
          </button>

          {showAdvanced && (
            <div className="advanced-options">
              <div className="setting-checkbox">
                <input
                  id="denoise"
                  type="checkbox"
                  checked={settings.enableDenoise}
                  onChange={() => handleToggle('enableDenoise')}
                />
                <label htmlFor="denoise" className="checkbox-label">
                  AI Denoise
                  <span className="help-text">Reduce noise while preserving detail</span>
                </label>
              </div>

              <div className="setting-checkbox">
                <input
                  id="lens-correction"
                  type="checkbox"
                  checked={settings.enableLensCorrection}
                  onChange={() => handleToggle('enableLensCorrection')}
                />
                <label htmlFor="lens-correction" className="checkbox-label">
                  Lens Correction
                  <span className="help-text">Correct lens distortion and vignetting</span>
                </label>
              </div>

              <div className="setting-checkbox">
                <input
                  id="chromatic-correction"
                  type="checkbox"
                  checked={settings.enableChromaticCorrection}
                  onChange={() => handleToggle('enableChromaticCorrection')}
                />
                <label htmlFor="chromatic-correction" className="checkbox-label">
                  Chromatic Aberration Correction
                  <span className="help-text">Fix color fringing on edges</span>
                </label>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn btn-secondary" onClick={onBack}>
          ← Back
        </button>
        <button
          className="btn btn-primary"
          onClick={() => onExport(settings)}
          disabled={!isValid}
        >
          Start Processing →
        </button>
      </div>
    </div>
  );
};

export default ExportSettings;