"""
Blender AI Copilot - Main Backend Server
FastAPI server for multimodal AI copilot functionality
"""

import asyncio
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from services.context_fusion import ContextFusionEngine
from services.screen_capture import ScreenCaptureService
from services.keyboard_hook import KeyboardHookService
from services.mouse_tracking import MouseTrackingService
from services.voice_recording import VoiceRecordingService
from models.session import SessionData, SessionManager

app = FastAPI(title="Blender AI Copilot Backend", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
context_engine: Optional[ContextFusionEngine] = None
session_manager: Optional[SessionManager] = None
active_session_id: Optional[str] = None


class Message(BaseModel):
    content: str
    type: str = "user"


class BlenderState(BaseModel):
    selected_objects: list
    active_mode: str
    scene_name: str
    frame_current: int
    render_engine: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global context_engine, session_manager
    context_engine = ContextFusionEngine()
    session_manager = SessionManager()
    print("✓ Backend services initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    global context_engine, session_manager
    if context_engine:
        await context_engine.shutdown()
    if session_manager:
        session_manager.cleanup()
    print("✓ Backend services shutdown")


@app.get("/")
async def root():
    return {
        "name": "Blender AI Copilot Backend",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "context_engine": context_engine is not None,
            "session_manager": session_manager is not None
        }
    }


@app.post("/session/start")
async def start_session(blender_version: str = "4.5", project_name: str = ""):
    """Start a new AI session"""
    global session_manager, active_session_id
    
    if not session_manager:
        return {"error": "Session manager not initialized"}
    
    session_id = session_manager.start_session(blender_version, project_name)
    active_session_id = session_id
    
    return {
        "session_id": session_id,
        "status": "started",
        "blender_version": blender_version,
        "project_name": project_name
    }


@app.post("/session/end")
async def end_session():
    """End current session"""
    global session_manager, active_session_id
    
    if not session_manager or not active_session_id:
        return {"error": "No active session"}
    
    success = session_manager.end_session()
    active_session_id = None
    
    return {"status": "ended" if success else "failed"}


@app.post("/session/blender_state")
async def update_blender_state(state: BlenderState):
    """Update Blender state in current session"""
    global session_manager, active_session_id
    
    if not session_manager or not active_session_id:
        return {"error": "No active session"}
    
    session_manager.save_blender_state(state.dict())
    
    return {"status": "updated"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for realtime communication"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process different message types
            msg_type = message_data.get("type")
            
            if msg_type == "keyboard_event":
                if context_engine and active_session_id:
                    context_engine.process_keyboard_event(
                        active_session_id, 
                        message_data.get("data", {})
                    )
            
            elif msg_type == "mouse_event":
                if context_engine and active_session_id:
                    context_engine.process_mouse_event(
                        active_session_id,
                        message_data.get("data", {})
                    )
            
            elif msg_type == "voice_transcript":
                if context_engine and active_session_id:
                    context_engine.process_voice_event(
                        active_session_id,
                        message_data.get("data", {})
                    )
            
            elif msg_type == "screen_capture":
                if context_engine and active_session_id:
                    context_engine.process_screen_event(
                        active_session_id,
                        message_data.get("data", {})
                    )
            
            elif msg_type == "query":
                # Handle AI query
                if context_engine:
                    response = await context_engine.generate_response(
                        message_data.get("query", "")
                    )
                    await websocket.send_json({
                        "type": "ai_response",
                        "data": response
                    })
            
            # Acknowledge receipt
            await websocket.send_json({
                "type": "ack",
                "message_id": message_data.get("id")
            })
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.post("/api/ocr/process")
async def process_ocr(image: UploadFile = File(...)):
    """Process OCR on uploaded image"""
    from ocr_service.ocr import OCRService
    
    ocr = OCRService()
    contents = await image.read()
    
    # Save temporarily and process
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    result = ocr.extract_text_from_image(tmp_path)
    
    # Cleanup
    import os
    os.unlink(tmp_path)
    
    return {"text_regions": result}


@app.post("/api/context/query")
async def query_context(query: str, session_id: Optional[str] = None):
    """Query context from current or specified session"""
    global context_engine, session_manager
    
    if not context_engine:
        return {"error": "Context engine not initialized"}
    
    target_session = session_id or active_session_id
    if not target_session:
        return {"error": "No session available"}
    
    response = await context_engine.generate_response(query, target_session)
    
    return {"response": response}


def main():
    """Run the backend server"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
