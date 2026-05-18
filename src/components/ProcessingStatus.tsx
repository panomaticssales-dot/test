/**
 * Real-time processing status display component.
 */

import React, { useEffect } from "react";
import { JobStatus } from "../utils/backend";
import "./ProcessingStatus.css";

interface ProcessingStatusProps {
  jobStatus: JobStatus | null;
  onStatusUpdate: (status: JobStatus) => void;
}

export const ProcessingStatusComponent: React.FC<ProcessingStatusProps> = (
  { jobStatus, onStatusUpdate }
) => {
  useEffect(() => {
    if (!jobStatus) return;

    const timer = setInterval(() => {
      onStatusUpdate(jobStatus);
    }, 1000); // Poll every second

    return () => clearInterval(timer);
  }, [jobStatus, onStatusUpdate]);

  if (!jobStatus) {
    return null;
  }

  const isComplete = jobStatus.status === "complete";
  const isError = jobStatus.status === "error";

  return (
    <div className="processing-status">
      <div className="status-header">
        <h3>Processing Status</h3>
        <span className={`status-badge ${jobStatus.status}`}>{jobStatus.status.toUpperCase()}</span>
      </div>

      <div className="progress-container">
        <div className="progress-bar-wrapper">
          <div className="progress-bar" style={{ width: `${jobStatus.progress}%` }} />
        </div>
        <span className="progress-text">{jobStatus.progress}%</span>
      </div>

      <div className="logs-container">
        <h4>Processing Logs</h4>
        <div className="logs-content">
          {jobStatus.logs.map((log, index) => (
            <div key={index} className="log-entry">
              <span className="log-timestamp">[{new Date().toLocaleTimeString()}]</span>
              <span className="log-message">{log}</span>
            </div>
          ))}
        </div>
      </div>

      {jobStatus.error_message && (
        <div className="error-message">
          <strong>Error:</strong> {jobStatus.error_message}
        </div>
      )}

      {isComplete && jobStatus.output_files && (
        <div className="output-files">
          <h4>Output Files</h4>
          <ul>
            {jobStatus.output_files.map((file, index) => (
              <li key={index}>{file}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
