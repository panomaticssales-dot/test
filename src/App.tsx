/**
 * Main App component with Tauri backend integration.
 */

import { useState, useEffect } from "react";
import { useBackend } from "./hooks/useBackend";
import { BackendStatus } from "./components/BackendStatus";
import { ProcessingStatusComponent } from "./components/ProcessingStatus";
import { DragDropZone } from "./components/DragDropZone";
import { ImageGrouping } from "./components/ImageGrouping";
import { ExportSettings } from "./components/ExportSettings";
import "./App.css";

type AppStep = "import" | "grouping" | "settings" | "processing";

function App() {
  const [
    currentStep,
    setCurrentStep,
  ] = useState<AppStep>("import");
  const [importedPath, setImportedPath] = useState<string>("");
  const [outputPath, setOutputPath] = useState<string>("");
  const [advancedOptions, setAdvancedOptions] = useState<any>({});

  const {
    backendHealthy,
    isInitializing,
    isAnalyzing,
    isProcessing,
    analysisResult,
    processingJobId,
    jobStatus,
    error,
    analyzeImages,
    startProcessing,
    pollJobStatus,
  } = useBackend();

  // Poll job status when processing
  useEffect(() => {
    if (!processingJobId) return;

    const interval = setInterval(() => {
      pollJobStatus(processingJobId);
    }, 1000);

    return () => clearInterval(interval);
  }, [processingJobId, pollJobStatus]);

  // Handle import
  const handleImport = async (folderPath: string) => {
    setImportedPath(folderPath);
    await analyzeImages(folderPath);
    setCurrentStep("grouping");
  };

  // Handle next step from grouping
  const handleGroupingNext = () => {
    setCurrentStep("settings");
  };

  // Handle start processing
  const handleStartProcessing = async (settings: any, outputPath: string) => {
    setOutputPath(outputPath);
    setAdvancedOptions(settings);
    await startProcessing(importedPath, outputPath, settings);
    setCurrentStep("processing");
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🎨 HDR Blender</h1>
          <p>Professional exposure fusion for photographers</p>
        </div>
        <BackendStatus healthy={backendHealthy} loading={isInitializing} />
      </header>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      <main className="app-main">
        {/* Step indicators */}
        <div className="step-indicator">
          <button
            className={`step-dot ${currentStep === "import" ? "active" : ""} ${currentStep !== "import" ? "completed" : ""}`}
            onClick={() => setCurrentStep("import")}
          >
            1
          </button>
          <div className="step-line" />
          <button
            className={`step-dot ${currentStep === "grouping" ? "active" : ""} ${["settings", "processing"].includes(currentStep) ? "completed" : ""}`}
            onClick={() => analysisResult && setCurrentStep("grouping")}
          >
            2
          </button>
          <div className="step-line" />
          <button
            className={`step-dot ${currentStep === "settings" ? "active" : ""} ${currentStep === "processing" ? "completed" : ""}`}
            onClick={() => analysisResult && setCurrentStep("settings")}
          >
            3
          </button>
          <div className="step-line" />
          <button className={`step-dot ${currentStep === "processing" ? "active" : ""}`}>
            4
          </button>
        </div>

        {/* Step content */}
        <div className="step-content">
          {currentStep === "import" && (
            <DragDropZone
              onImport={handleImport}
              loading={isAnalyzing}
              disabled={!backendHealthy}
            />
          )}

          {currentStep === "grouping" && analysisResult && (
            <ImageGrouping
              analysisResult={analysisResult}
              onNext={handleGroupingNext}
            />
          )}

          {currentStep === "settings" && analysisResult && (
            <ExportSettings
              onStartProcessing={handleStartProcessing}
              loading={isProcessing}
            />
          )}

          {currentStep === "processing" && jobStatus && (
            <ProcessingStatusComponent
              jobStatus={jobStatus}
              onStatusUpdate={(status) => {
                // Status is already updated via pollJobStatus
              }}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
