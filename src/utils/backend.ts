/**
 * Backend API client for communicating with Python HDR processing engine.
 */

import { invoke } from "@tauri-apps/api/tauri";

export interface BracketGroupInfo {
  angle: number;
  images: number;
  exposures: number[];
  filenames: string[];
}

export interface AnalysisResult {
  status: string;
  groups: BracketGroupInfo[];
  total_images: number;
}

export interface ProcessRequest {
  folder_path: string;
  output_path: string;
  enable_denoise: boolean;
  enable_ghost_removal: boolean;
  enable_lens_correction: boolean;
  enable_chromatic_correction: boolean;
}

export interface ProcessResponse {
  status: string;
  job_id: string;
}

export interface JobStatus {
  status: string;
  progress: number;
  logs: string[];
  error_message?: string;
  output_files?: string[];
}

/**
 * Backend API client
 */
export class BackendClient {
  /**
   * Start Python backend process
   */
  static async startBackend(): Promise<string> {
    return await invoke("start_backend");
  }

  /**
   * Check if backend is healthy
   */
  static async checkHealth(): Promise<boolean> {
    return await invoke("check_backend_health");
  }

  /**
   * Analyze images in folder and detect bracket groups
   */
  static async analyzeImages(folderPath: string): Promise<AnalysisResult> {
    return await invoke("analyze_images", { folderPath });
  }

  /**
   * Start processing bracket groups
   */
  static async processImages(request: ProcessRequest): Promise<ProcessResponse> {
    return await invoke("process_images", { request });
  }

  /**
   * Get processing job status
   */
  static async getJobStatus(jobId: string): Promise<JobStatus> {
    return await invoke("get_job_status", { jobId });
  }

  /**
   * Stop backend process
   */
  static async stopBackend(): Promise<string> {
    return await invoke("stop_backend");
  }
}
