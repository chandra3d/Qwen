// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct AppState {
    connected: bool,
    recording: bool,
    session_id: Option<String>,
}

fn main() {
    tauri::Builder::default()
        .manage(AppState {
            connected: false,
            recording: false,
            session_id: None,
        })
        .invoke_handler(tauri::generate_handler![
            connect_backend,
            disconnect_backend,
            start_recording,
            stop_recording,
            get_session_status
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn connect_backend(state: tauri::State<AppState>) -> Result<bool, String> {
    // TODO: Implement actual WebSocket connection to backend
    println!("Connecting to backend...");
    Ok(true)
}

#[tauri::command]
fn disconnect_backend(state: tauri::State<AppState>) -> Result<bool, String> {
    println!("Disconnecting from backend...");
    Ok(true)
}

#[tauri::command]
fn start_recording(state: tauri::State<AppState>) -> Result<bool, String> {
    println!("Starting recording...");
    Ok(true)
}

#[tauri::command]
fn stop_recording(state: tauri::State<AppState>) -> Result<bool, String> {
    println!("Stopping recording...");
    Ok(true)
}

#[tauri::command]
fn get_session_status(state: tauri::State<AppState>) -> Result<AppState, String> {
    Ok(AppState {
        connected: state.connected,
        recording: state.recording,
        session_id: state.session_id.clone(),
    })
}
