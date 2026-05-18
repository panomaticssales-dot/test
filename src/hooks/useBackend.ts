/**
 * React hook for managing backend connection and processing.
 */

import { useState, useEffect, useCallback } from "react";
import { BackendClient, AnalysisResult, ProcessResponse, JobStatus } from "../utils/backend";

export interface UseBackendState {
  backendHealthy: boolean;
  isInitializing: boolean;
  isAnalyzing: boolean;
  isProcessing: boolean;
  analysisResult: AnalysisResult | null;
  processingJobId: string | null;
  jobStatus: JobStatus | null;
  error: string | null;
}

export function useBackend(): UseBackendState & {
  initializeBackend: () => Promise<void>;
  analyzeImages: (folderPath: string) => Promise<void>;
  startProcessing: (folderPath: string, outputPath: string, advancedOptions: any) => Promise<void>;
  pollJobStatus: (jobId: string) => Promise<void>;
} {
  const [state, setState] = useState<UseBackendState>({
    backendHealthy: false,
    isInitializing: false,
    isAnalyzing: false,
    isProcessing: false,
    analysisResult: null,
    processingJobId: null,
    jobStatus: null,
    error: null,
  });

  // Initialize backend
  useEffect(() => {
    const initialize = async () => {
      setState((prev) => ({ ...prev, isInitializing: true }));
      try {
        // Check if already running
        const healthy = await BackendClient.checkHealth();
        if (!healthy) {
          // Start backend
          await BackendClient.startBackend();
        }
        setState((prev) => ({ ...prev, backendHealthy: true, isInitializing: false }));
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error("Backend initialization failed:", errorMsg);
        setState((prev) => ({
          ...prev,
          backendHealthy: false,
          isInitializing: false,
          error: errorMsg,
        }));
      }
    };

    initialize();
  }, []);

  // Analyze images
  const analyzeImages = useCallback(async (folderPath: string) => {
    setState((prev) => ({ ...prev, isAnalyzing: true, error: null }));
    try {
      const result = await BackendClient.analyzeImages(folderPath);
      setState((prev) => ({ ...prev, analysisResult: result, isAnalyzing: false }));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setState((prev) => ({
        ...prev,
        isAnalyzing: false,
        error: errorMsg,
      }));
    }
  }, []);

  // Start processing
  const startProcessing = useCallback(
    async (folderPath: string, outputPath: string, advancedOptions: any) => {
      setState((prev) => ({ ...prev, isProcessing: true, error: null }));
      try {
        const response = await BackendClient.processImages({
          folder_path: folderPath,
          output_path: outputPath,
          enable_denoise: advancedOptions.denoise || false,
          enable_ghost_removal: advancedOptions.ghostRemoval || false,
          enable_lens_correction: advancedOptions.lensCorrection || false,
          enable_chromatic_correction: advancedOptions.chromaticCorrection || false,
        });
        setState((prev) => ({
          ...prev,
          processingJobId: response.job_id,
          isProcessing: false,
        }));
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        setState((prev) => ({
          ...prev,
          isProcessing: false,
          error: errorMsg,
        }));
      }
    },
    []
  );

  // Poll job status
  const pollJobStatus = useCallback(async (jobId: string) => {
    try {
      const status = await BackendClient.getJobStatus(jobId);
      setState((prev) => ({ ...prev, jobStatus: status }));
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setState((prev) => ({
        ...prev,
        error: errorMsg,
      }));
    }
  }, []);

  return {
    ...state,
    initializeBackend: async () => {
      // Already initialized in useEffect
    },
    analyzeImages,
    startProcessing,
    pollJobStatus,
  };
}
