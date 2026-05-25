"""
Session Manager
Handles Universal AI Session Format storage and retrieval
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid


class SessionManager:
    """
    Manages AI sessions with Universal AI Session Format:
    .session/
        metadata.json
        timeline.jsonl
        audio/
        frames/
        embeddings/
        blender_state/
    """
    
    def __init__(self, base_path: str = "./sessions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.active_sessions: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
    
    async def create_session(self, name: str, description: str = "") -> Dict:
        """Create a new session with the universal format"""
        async with self._lock:
            session_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            session_path = self.base_path / session_id
            session_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (session_path / "audio").mkdir(exist_ok=True)
            (session_path / "frames").mkdir(exist_ok=True)
            (session_path / "embeddings").mkdir(exist_ok=True)
            (session_path / "blender_state").mkdir(exist_ok=True)
            
            # Create metadata.json
            metadata = {
                "id": session_id,
                "name": name,
                "description": description,
                "created_at": timestamp,
                "updated_at": timestamp,
                "blender_version": None,
                "platform": "windows",
                "total_events": 0,
                "duration_seconds": 0
            }
            
            metadata_path = session_path / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create empty timeline.jsonl
            timeline_path = session_path / "timeline.jsonl"
            timeline_path.touch()
            
            # Store in active sessions
            self.active_sessions[session_id] = {
                "metadata": metadata,
                "path": session_path,
                "event_count": 0
            }
            
            return metadata
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session metadata"""
        session_path = self.base_path / session_id
        
        if not session_path.exists():
            return None
        
        metadata_path = session_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)
        
        return None
    
    async def add_timeline_event(self, session_id: str, event: Dict) -> bool:
        """Add an event to the timeline"""
        session_data = self.active_sessions.get(session_id)
        
        if not session_data:
            # Try to load from disk
            session_path = self.base_path / session_id
            if not session_path.exists():
                return False
            
            metadata_path = session_path / "metadata.json"
            if not metadata_path.exists():
                return False
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            session_data = {
                "metadata": metadata,
                "path": session_path,
                "event_count": metadata.get("total_events", 0)
            }
        
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        
        # Append to timeline.jsonl
        timeline_path = session_data["path"] / "timeline.jsonl"
        with open(timeline_path, 'a') as f:
            f.write(json.dumps(event) + "\n")
        
        # Update event count
        session_data["event_count"] += 1
        
        # Update metadata
        session_data["metadata"]["total_events"] = session_data["event_count"]
        session_data["metadata"]["updated_at"] = datetime.now().isoformat()
        
        metadata_path = session_data["path"] / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(session_data["metadata"], f, indent=2)
        
        return True
    
    async def get_timeline(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get timeline events for a session"""
        session_path = self.base_path / session_id
        timeline_path = session_path / "timeline.jsonl"
        
        if not timeline_path.exists():
            return []
        
        events = []
        with open(timeline_path, 'r') as f:
            lines = f.readlines()
            
            # Get last N events
            start_idx = max(0, len(lines) - limit)
            for line in lines[start_idx:]:
                if line.strip():
                    events.append(json.loads(line))
        
        return events
    
    async def save_audio(self, session_id: str, audio_data: bytes, filename: str = None) -> str:
        """Save audio file to session"""
        if filename is None:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.wav"
        
        session_path = self.base_path / session_id
        audio_path = session_path / "audio" / filename
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        return str(audio_path)
    
    async def save_frame(self, session_id: str, frame_data: bytes, filename: str = None) -> str:
        """Save screenshot frame to session"""
        if filename is None:
            filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
        
        session_path = self.base_path / session_id
        frames_path = session_path / "frames" / filename
        
        with open(frames_path, 'wb') as f:
            f.write(frame_data)
        
        return str(frames_path)
    
    async def save_blender_state(self, session_id: str, state: Dict, filename: str = None) -> str:
        """Save Blender state snapshot"""
        if filename is None:
            filename = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        session_path = self.base_path / session_id
        state_path = session_path / "blender_state" / filename
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        
        return str(state_path)
    
    async def save_embeddings(self, session_id: str, embeddings: List[float], metadata: Dict = None) -> str:
        """Save embeddings to session"""
        filename = f"emb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
        
        session_path = self.base_path / session_id
        emb_path = session_path / "embeddings" / filename
        
        data = {
            "embeddings": embeddings,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        with open(emb_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(emb_path)
    
    async def list_sessions(self) -> List[Dict]:
        """List all available sessions"""
        sessions = []
        
        for session_dir in self.base_path.iterdir():
            if session_dir.is_dir():
                metadata_path = session_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        sessions.append(metadata)
        
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return sessions
    
    async def close(self):
        """Cleanup resources"""
        self.active_sessions.clear()
