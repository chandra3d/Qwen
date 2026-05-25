"""
Session Data Models
Data structures for session management
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class SessionData(BaseModel):
    """Session data model"""
    session_id: str
    created_at: str
    updated_at: Optional[str] = None
    blender_version: str = "4.5"
    project_name: str = ""
    metadata: Dict[str, Any] = {}


class TimelineEvent(BaseModel):
    """Timeline event model"""
    id: Optional[int] = None
    session_id: str
    timestamp: str
    event_type: str
    data: Dict[str, Any]


class BlenderStateSnapshot(BaseModel):
    """Blender state snapshot model"""
    id: Optional[int] = None
    session_id: str
    timestamp: str
    state_data: Dict[str, Any]


class TranscriptionRecord(BaseModel):
    """Voice transcription record model"""
    id: Optional[int] = None
    session_id: str
    timestamp: str
    text: str
    audio_path: str
    confidence: float = 1.0


class ScreenFrameRecord(BaseModel):
    """Screen frame record model"""
    id: Optional[int] = None
    session_id: str
    timestamp: str
    frame_path: str
    fps: float = 1.0


# Import from memory_db
try:
    from memory_db.database import SessionManager
except ImportError:
    # Fallback if running from different directory
    class SessionManager:
        """Placeholder SessionManager for imports"""
        pass
