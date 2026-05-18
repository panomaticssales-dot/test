import React, { useState, useEffect } from 'react';
import './ProcessingStatus.css';

interface ProcessingStep {
  name: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  progress: number;
}

interface ProcessingStatusProps {
  isProcessing: boolean;
  logs: string[];
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ isProcessing, logs }) => {
  const [steps, setSteps] = useState<ProcessingStep[]>([
    { name: 'Analyzing Images', status: 'pending', progress: 0 },
    { name: 'Aligning Exposures', status: 'pending', progress: 0 },
    { name: 'Blending Brackets', status: 'pending', progress: 0 },
    { name: 'Exporting TIFFs', status: 'pending', progress: 0 },
  ]);

  const [overallProgress, setOverallProgress] = useState(0);

  useEffect(() => {
    if (isProcessing) {
      // Simulate processing steps
      const interval = setInterval(() => {
        setSteps((prevSteps) =>
          prevSteps.map((step, idx) => {
            const activeStep = prevSteps.findIndex((s) => s.status === 'active');
            const completeCount = prevSteps.filter((s) => s.status === 'complete').length;

            if (idx < completeCount) {
              return step;
            } else if (idx === completeCount && step.status === 'pending') {
              return { ...step, status: 'active', progress: Math.min(step.progress + Math.random() * 15, 95) };
            } else if (idx === completeCount && step.status === 'active') {
              if (step.progress >= 90) {
                return { ...step, status: 'complete', progress: 100 };
              }
              return { ...step, progress: Math.min(step.progress + Math.random() * 10, 95) };
            }
            return step;
          })
        );
      }, 500);

      return () => clearInterval(interval);
    }
  }, [isProcessing]);

  useEffect(() => {
    const totalProgress = steps.reduce((sum, step) => sum + step.progress, 0) / steps.length;
    setOverallProgress(totalProgress);
  }, [steps]);

  const isComplete = steps.every((step) => step.status === 'complete');

  return (
    <div className="processing-status">
      <div className="status-header">
        <h2>{isComplete ? '✓ Processing Complete!' : 'Processing Images...'}</h2>
        <p>
          {isComplete
            ? 'Your HDR images have been successfully created.'
            : 'This may take a few minutes depending on the number of images.'}
        </p>
      </div>

      {/* Overall Progress */}
      <div className="overall-progress">
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${overallProgress}%` }} />
          </div>
        </div>
        <div className="progress-text">
          <span>{Math.round(overallProgress)}%</span>
          <span>Complete</span>
        </div>
      </div>

      {/* Processing Steps */}
      <div className="processing-steps">
        {steps.map((step, idx) => (
          <div key={idx} className={`step ${step.status}`}>
            <div className="step-header">
              <div className="step-indicator">
                {step.status === 'complete' ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : step.status === 'active' ? (
                  <div className="spinner" />
                ) : (
                  <div className="dot" />
                )}
              </div>
              <span className="step-name">{step.name}</span>
            </div>
            <div className="step-progress-bar">
              <div
                className="step-progress-fill"
                style={{ width: `${step.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Logs */}
      <div className="logs-section">
        <h3>Processing Logs</h3>
        <div className="logs-container">
          {logs.length > 0 ? (
            logs.map((log, idx) => (
              <div key={idx} className="log-entry">
                <span className="log-time">{new Date().toLocaleTimeString()}</span>
                <span className="log-message">{log}</span>
              </div>
            ))
          ) : (
            <div className="log-entry empty">
              <span className="log-message">Waiting for processing to start...</span>
            </div>
          )}
        </div>
      </div>

      {isComplete && (
        <div className="completion-actions">
          <button className="btn btn-primary">Open Output Folder</button>
          <button className="btn btn-secondary">Process More Images</button>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;