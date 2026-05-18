import React, { useState } from 'react';
import './App.css';
import DragDropZone from './components/DragDropZone';
import ImageGrouping from './components/ImageGrouping';
import ExportSettings from './components/ExportSettings';
import ProcessingStatus from './components/ProcessingStatus';

interface ImageGroup {
  angle: number;
  exposures: number;
  images: string[];
}

type WorkflowStep = 'import' | 'grouping' | 'settings' | 'processing';

const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('import');
  const [importedFiles, setImportedFiles] = useState<File[]>([]);
  const [groups, setGroups] = useState<ImageGroup[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  const handleImport = (files: FileList) => {
    const fileArray = Array.from(files);
    setImportedFiles(fileArray);
    
    // Simulate grouping detection
    const simulatedGroups: ImageGroup[] = [];
    let angleNum = 1;
    let currentAngle: ImageGroup | null = null;

    fileArray.forEach((file, idx) => {
      if (!currentAngle || currentAngle.images.length >= 3) {
        if (currentAngle) simulatedGroups.push(currentAngle);
        currentAngle = {
          angle: angleNum++,
          exposures: Math.random() > 0.5 ? 3 : 5,
          images: [],
        };
      }
      currentAngle!.images.push(file.name);
    });

    if (currentAngle) {
      simulatedGroups.push(currentAngle);
    }

    setGroups(simulatedGroups);
    setLogs([`Detected ${simulatedGroups.length} angle groups from ${fileArray.length} images`]);
    setCurrentStep('grouping');
  };

  const handleContinueToSettings = () => {
    setCurrentStep('settings');
  };

  const handleExport = (settings: any) => {
    setIsProcessing(true);
    setCurrentStep('processing');
    setLogs(['Starting HDR processing pipeline...', 'Step 1: Analyzing image metadata...']);

    // Simulate processing
    setTimeout(() => {
      setLogs((prev) => [...prev, 'Step 2: Detecting exposure brackets...']);
    }, 2000);

    setTimeout(() => {
      setLogs((prev) => [...prev, 'Step 3: Aligning exposures...']);
    }, 4000);

    setTimeout(() => {
      setLogs((prev) => [...prev, 'Step 4: Blending exposures using Mertens algorithm...']);
    }, 6000);

    setTimeout(() => {
      setLogs((prev) => [...prev, 'Step 5: Exporting 16-bit TIFF files...']);
    }, 8000);

    setTimeout(() => {
      setLogs((prev) => [...prev, '✓ Processing complete!', 'Output saved to: ' + settings.outputPath]);
      setIsProcessing(false);
    }, 10000);
  };

  const handleBackToImport = () => {
    setCurrentStep('import');
    setImportedFiles([]);
    setGroups([]);
    setLogs([]);
  };

  return (
    <div className="app">
      <div className="app-header">
        <div className="logo-section">
          <h1>HDR Blender</h1>
          <p>Professional exposure fusion for photographers</p>
        </div>
        <div className="step-indicator">
          <div className={`step ${currentStep === 'import' ? 'active' : 'complete'}`}>
            <span>1</span>
            <p>Import</p>
          </div>
          <div className="step-connector" />
          <div className={`step ${currentStep === 'grouping' ? 'active' : currentStep === 'import' ? '' : 'complete'}`}>
            <span>2</span>
            <p>Group</p>
          </div>
          <div className="step-connector" />
          <div className={`step ${currentStep === 'settings' ? 'active' : currentStep === 'import' || currentStep === 'grouping' ? '' : 'complete'}`}>
            <span>3</span>
            <p>Configure</p>
          </div>
          <div className="step-connector" />
          <div className={`step ${currentStep === 'processing' ? 'active' : ''}`}>
            <span>4</span>
            <p>Process</p>
          </div>
        </div>
      </div>

      <div className="app-content">
        {currentStep === 'import' && (
          <DragDropZone onImport={handleImport} isProcessing={false} />
        )}

        {currentStep === 'grouping' && (
          <ImageGrouping groups={groups} onContinue={handleContinueToSettings} />
        )}

        {currentStep === 'settings' && (
          <ExportSettings
            onExport={handleExport}
            onBack={() => setCurrentStep('grouping')}
          />
        )}

        {currentStep === 'processing' && (
          <ProcessingStatus isProcessing={isProcessing} logs={logs} />
        )}
      </div>
    </div>
  );
};

export default App;