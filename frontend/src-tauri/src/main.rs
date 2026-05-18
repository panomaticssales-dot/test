#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

use tauri::Manager;
use std::path::PathBuf;

#[tauri::command]
fn greet(name: &str) -> String {
  format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn process_images(
  image_paths: Vec<String>,
  output_path: String,
  settings: serde_json::Value,
) -> Result<String, String> {
  // This will be called by the frontend when processing starts
  // The actual Python backend will handle the heavy lifting
  println!("Processing {} images", image_paths.len());
  println!("Output path: {}", output_path);
  println!("Settings: {:?}", settings);
  
  Ok(format!("Processing {} images", image_paths.len()))
}

#[tauri::command]
fn select_folder(window: tauri::Window) -> Result<String, String> {
  // Open file dialog for folder selection
  match tauri::api::dialog::blocking::FileDialogBuilder::new()
    .pick_folder() {
    Some(path) => Ok(path.to_string_lossy().to_string()),
    None => Err("No folder selected".to_string()),
  }
}

#[tauri::command]
fn analyze_images(folder_path: String) -> Result<serde_json::Value, String> {
  // Scan folder and return image metadata
  println!("Analyzing images in: {}", folder_path);
  
  // This would be expanded to actually analyze images
  Ok(serde_json::json!({
    "total_images": 0,
    "angles": [],
    "status": "ready"
  }))
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![
      greet,
      process_images,
      select_folder,
      analyze_images
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
