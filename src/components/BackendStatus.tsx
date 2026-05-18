/**
 * Backend status indicator component.
 */

import React from "react";
import "./BackendStatus.css";

interface BackendStatusProps {
  healthy: boolean;
  loading?: boolean;
}

export const BackendStatus: React.FC<BackendStatusProps> = ({ healthy, loading = false }) => {
  return (
    <div className="backend-status">
      <div className={`status-indicator ${healthy ? "healthy" : "unhealthy"} ${loading ? "loading" : ""}`} />
      <span className="status-text">
        {loading ? "Initializing..." : healthy ? "Backend Ready" : "Backend Offline"}
      </span>
    </div>
  );
};
