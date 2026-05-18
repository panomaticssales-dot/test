// Tauri IPC bridge for HDR Blender
#![cfg_attr(all(not(debug_assertions), target_os = "windows"), windows_subsystem = "windows")]

use tauri::{Manager, State};
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use reqwest::Client;
use std::process::{Command, Stdio};
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

/// Global backend URL
const BACKEND_URL: &str = "http://localhost:8000";

/// Analysis result from backend
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AnalysisResult {
    pub status: String,
    pub groups: Vec<BracketGroupInfo>,
    pub total_images: usize,
}

/// Bracket group information
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BracketGroupInfo {
    pub angle: usize,
    pub images: usize,
    pub exposures: Vec<f32>,
    pub filenames: Vec<String>,
}

/// Processing request
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProcessRequest {
    pub folder_path: String,
    pub output_path: String,
    pub enable_denoise: bool,
    pub enable_ghost_removal: bool,
    pub enable_lens_correction: bool,
    pub enable_chromatic_correction: bool,
}

/// Processing response
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProcessResponse {
    pub status: String,
    pub job_id: String,
}

/// Job status
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct JobStatus {
    pub status: String,
    pub progress: i32,
    pub logs: Vec<String>,
    pub error_message: Option<String>,
    pub output_files: Option<Vec<String>>,
}

/// Shared state for managing backend process
pub struct BackendState {
    pub process: Mutex<Option<std::process::Child>>,
    pub client: Client,
}

impl Default for BackendState {
    fn default() -> Self {
        Self {
            process: Mutex::new(None),
            client: Client::new(),
        }
    }
}

/// Start Python backend process
#[tauri::command]
async fn start_backend(
    backend_state: State<'_, BackendState>,
) -> Result<String, String> {
    // Check if backend is already running
    let client = Client::new();
    match client.get(&format!("{}/health", BACKEND_URL)).send().await {
        Ok(resp) if resp.status().is_success() => {
            return Ok("Backend already running".to_string());
        }
        _ => {}
    }

    // Spawn backend process
    let mut process = Command::new("python")
        .args(&["-m", "src.main"])
        .current_dir("./backend")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?
        ;

    let pid = process.id();
    *backend_state.process.lock().unwrap() = Some(process);

    // Wait for backend to be ready
    for i in 0..30 {
        let client = Client::new();
        if client.get(&format!("{}/health", BACKEND_URL)).send().await.is_ok() {
            return Ok(format!("Backend started (PID: {})", pid));
        }
        thread::sleep(Duration::from_millis(500));
    }

    Err("Backend failed to start within timeout".to_string())
}

/// Analyze images in a folder
#[tauri::command]
async fn analyze_images(
    folder_path: String,
    backend_state: State<'_, BackendState>,
) -> Result<AnalysisResult, String> {
    let url = format!("{}/api/analyze?folder_path={}", BACKEND_URL, urlencoding::encode(&folder_path));
    
    backend_state
        .client
        .post(&url)
        .send()
        .await
        .map_err(|e| format!("Failed to analyze images: {}", e))?
        .json::<AnalysisResult>()
        .await
        .map_err(|e| format!("Failed to parse analysis result: {}", e))
}

/// Start processing bracket groups
#[tauri::command]
async fn process_images(
    request: ProcessRequest,
    backend_state: State<'_, BackendState>,
) -> Result<ProcessResponse, String> {
    let url = format!(
        "{}/api/process?folder_path={}&output_path={}&enable_denoise={}&enable_ghost_removal={}&enable_lens_correction={}&enable_chromatic_correction={}",
        BACKEND_URL,
        urlencoding::encode(&request.folder_path),
        urlencoding::encode(&request.output_path),
        request.enable_denoise,
        request.enable_ghost_removal,
        request.enable_lens_correction,
        request.enable_chromatic_correction,
    );

    backend_state
        .client
        .post(&url)
        .send()
        .await
        .map_err(|e| format!("Failed to start processing: {}", e))?
        .json::<ProcessResponse>()
        .await
        .map_err(|e| format!("Failed to parse process response: {}", e))
}

/// Get processing job status
#[tauri::command]
async fn get_job_status(
    job_id: String,
    backend_state: State<'_, BackendState>,
) -> Result<JobStatus, String> {
    let url = format!("{}/api/status/{}", BACKEND_URL, job_id);

    backend_state
        .client
        .get(&url)
        .send()
        .await
        .map_err(|e| format!("Failed to get job status: {}", e))?
        .json::<JobStatus>()
        .await
        .map_err(|e| format!("Failed to parse job status: {}", e))
}

/// Stop backend process
#[tauri::command]
fn stop_backend(backend_state: State<BackendState>) -> Result<String, String> {
    if let Some(mut process) = backend_state.process.lock().unwrap().take() {
        process.kill().map_err(|e| format!("Failed to kill backend: {}", e))?;
        Ok("Backend stopped".to_string())
    } else {
        Err("Backend not running".to_string())
    }
}

/// Check if backend is healthy
#[tauri::command]
async fn check_backend_health(backend_state: State<'_, BackendState>) -> Result<bool, String> {
    match backend_state
        .client
        .get(&format!("{}/health", BACKEND_URL))
        .send()
        .await
    {
        Ok(resp) => Ok(resp.status().is_success()),
        Err(_) => Ok(false),
    }
}

fn main() {
    tauri::Builder::default()
        .manage(BackendState::default())
        .invoke_handler(tauri::generate_handler![
            start_backend,
            analyze_images,
            process_images,
            get_job_status,
            stop_backend,
            check_backend_health,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
