import React, { useState } from 'react';
import './ImageGrouping.css';

interface ImageGroup {
  angle: number;
  exposures: number;
  images: string[];
}

interface ImageGroupingProps {
  groups: ImageGroup[];
  onContinue: () => void;
}

const ImageGrouping: React.FC<ImageGroupingProps> = ({ groups, onContinue }) => {
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null);
  const totalImages = groups.reduce((sum, g) => sum + g.images.length, 0);

  return (
    <div className="image-grouping">
      <div className="grouping-header">
        <h2>Auto-Detected Bracket Groups</h2>
        <p>
          Found <strong>{groups.length} angle(s)</strong> with <strong>{totalImages} image(s)</strong>
        </p>
      </div>

      <div className="groups-container">
        {groups.length > 0 ? (
          groups.map((group) => (
            <div
              key={group.angle}
              className={`group-card ${selectedGroup === group.angle ? 'selected' : ''}`}
              onClick={() => setSelectedGroup(selectedGroup === group.angle ? null : group.angle)}
            >
              <div className="group-header">
                <div className="angle-badge">Angle {group.angle}</div>
                <div className="exposure-count">{group.exposures}-EV</div>
              </div>
              <div className="image-count">
                <span className="count">{group.images.length}</span>
                <span className="label">images</span>
              </div>
              {selectedGroup === group.angle && (
                <div className="group-details">
                  <div className="details-title">Images in this group:</div>
                  <ul className="image-list">
                    {group.images.map((img, idx) => (
                      <li key={idx}>{img}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>No images detected. Drag and drop images to get started.</p>
          </div>
        )}
      </div>

      {groups.length > 0 && (
        <div className="grouping-actions">
          <button className="btn btn-secondary" onClick={() => window.location.reload()}>
            ← Back
          </button>
          <button className="btn btn-primary" onClick={onContinue}>
            Continue to Export Settings →
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageGrouping;