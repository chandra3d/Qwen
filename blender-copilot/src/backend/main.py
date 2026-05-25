"""
Blender AI Copilot - Main FastAPI Server
Real-time multimodal context fusion for Blender workflows
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

from src.backend.services.context_fusion import ContextFusionEngine
from src.backend.services.screen_capture import ScreenCaptureService
from src.backend.services.keyboard_hook import KeyboardHookService
from src.backend.services.mouse_tracking import MouseTrackingService
from src.backend.services.voice_recording import VoiceRecordingService
from src.backend.models.session import SessionManager

app = FastAPI(
    title="Blender AI Copilot Backend",
    description="Multimodal context fusion engine for Blender workflows",
    version="0.1.0"
)

# CORS configuration for desktop client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
context_engine: Optional[ContextFusionEngine] = None
session_manager: Optional[SessionManager] = None
active_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize all services on startup"""
    global context_engine, session_manager
    
    context_engine = ContextFusionEngine()
    session_manager = SessionManager()
    
    # Initialize screen capture
    screen_service = ScreenCaptureService()
    await screen_service.start()
    
    # Initialize keyboard hook
    keyboard_service = KeyboardHookService(context_engine)
    keyboard_service.start()
    
    # Initialize mouse tracking
    mouse_service = MouseTrackingService(context_engine)
    mouse_service.start()
    
    # Initialize voice recording
    voice_service = VoiceRecordingService(context_engine)
    await voice_service.start()
    
    print("✅ All services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services on shutdown"""
    await context_engine.shutdown()
    await session_manager.close()


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
        "timestamp": datetime.now().isoformat(),
        "services": {
            "context_engine": context_engine is not None,
            "session_manager": session_manager is not None,
            "active_connections": len(active_connections)
        }
    }


@app.websocket("/ws/context")
async def websocket_context(websocket: WebSocket):
    """WebSocket endpoint for real-time context updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive data from client (Blender add-on or desktop client)
            data = await websocket.receive_json()
            
            # Process incoming context data
            if context_engine:
                processed_context = await context_engine.process_data(data)
                
                # Broadcast updated context to all connected clients
                await broadcast_context(processed_context)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client disconnected. Active connections: {len(active_connections)}")


@app.websocket("/ws/blender")
async def websocket_blender(websocket: WebSocket):
    """WebSocket endpoint for Blender add-on connection"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive Blender state updates
            blender_state = await websocket.receive_json()
            
            # Add Blender state to context
            if context_engine:
                await context_engine.add_blender_state(blender_state)
                
                # Get current fused context
                fused_context = context_engine.get_current_context()
                
                # Send back AI suggestions or acknowledgments
                response = {
                    "type": "acknowledgment",
                    "context_id": fused_context.get("id"),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(response)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Blender add-on disconnected. Active connections: {len(active_connections)}")


@app.post("/api/session/start")
async def start_session(session_name: str):
    """Start a new AI session"""
    if session_manager:
        session = await session_manager.create_session(session_name)
        return {"session_id": session["id"], "status": "started"}
    return {"error": "Session manager not initialized"}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_manager:
        session = await session_manager.get_session(session_id)
        return session
    return {"error": "Session manager not initialized"}


@app.get("/api/timeline/{session_id}")
async def get_timeline(session_id: str, limit: int = 100):
    """Get timeline events for a session"""
    if session_manager:
        events = await session_manager.get_timeline(session_id, limit)
        return {"events": events}
    return {"error": "Session manager not initialized"}


async def broadcast_context(context: dict):
    """Broadcast context update to all connected clients"""
    if not active_connections:
        return
    
    message = json.dumps({
        "type": "context_update",
        "data": context,
        "timestamp": datetime.now().isoformat()
    })
    
    # Send to all connected clients
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except:
            disconnected.append(connection)
    
    # Remove disconnected clients
    for conn in disconnected:
        active_connections.remove(conn)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
