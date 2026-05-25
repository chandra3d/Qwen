"""
Memory & Timeline Database System
Stores session data, embeddings, and context for AI retrieval
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import hashlib


class MemoryDatabase:
    """SQLite-based memory database for session storage"""
    
    def __init__(self, db_path: str = "copilot_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                blender_version TEXT,
                project_name TEXT,
                metadata JSON
            )
        ''')
        
        # Timeline events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                data JSON,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Blender state snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blender_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                state_data JSON,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Voice transcriptions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                text TEXT,
                audio_path TEXT,
                confidence REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Screen frames metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screen_frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                frame_path TEXT,
                fps REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        self.conn.commit()
    
    def create_session(self, session_id: str, blender_version: str = "4.5", 
                       project_name: str = "", metadata: Dict = None) -> bool:
        """Create a new session"""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO sessions (id, created_at, updated_at, blender_version, 
                                     project_name, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, now, now, blender_version, project_name, 
                  json.dumps(metadata or {})))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def add_timeline_event(self, session_id: str, event_type: str, 
                          data: Dict) -> bool:
        """Add an event to the timeline"""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO timeline_events (session_id, timestamp, event_type, data)
                VALUES (?, ?, ?, ?)
            ''', (session_id, timestamp, event_type, json.dumps(data)))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding timeline event: {e}")
            return False
    
    def save_blender_state(self, session_id: str, state_data: Dict) -> bool:
        """Save a Blender state snapshot"""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO blender_states (session_id, timestamp, state_data)
                VALUES (?, ?, ?)
            ''', (session_id, timestamp, json.dumps(state_data)))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving blender state: {e}")
            return False
    
    def add_transcription(self, session_id: str, text: str, 
                         audio_path: str, confidence: float = 1.0) -> bool:
        """Add voice transcription"""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO transcriptions (session_id, timestamp, text, 
                                           audio_path, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, timestamp, text, audio_path, confidence))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding transcription: {e}")
            return False
    
    def add_screen_frame(self, session_id: str, frame_path: str, 
                        fps: float = 1.0) -> bool:
        """Add screen frame metadata"""
        try:
            cursor = self.conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO screen_frames (session_id, timestamp, frame_path, fps)
                VALUES (?, ?, ?, ?)
            ''', (session_id, timestamp, frame_path, fps))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding screen frame: {e}")
            return False
    
    def get_session_timeline(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Retrieve timeline events for a session"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT timestamp, event_type, data 
                FROM timeline_events 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (session_id, limit))
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'timestamp': row[0],
                    'event_type': row[1],
                    'data': json.loads(row[2])
                })
            
            return events
        except Exception as e:
            print(f"Error getting timeline: {e}")
            return []
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary with all related data"""
        try:
            cursor = self.conn.cursor()
            
            # Get session info
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return None
            
            session = {
                'id': session_row[0],
                'created_at': session_row[1],
                'updated_at': session_row[2],
                'blender_version': session_row[3],
                'project_name': session_row[4],
                'metadata': json.loads(session_row[5])
            }
            
            # Get counts
            cursor.execute('SELECT COUNT(*) FROM timeline_events WHERE session_id = ?', 
                          (session_id,))
            session['event_count'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM blender_states WHERE session_id = ?', 
                          (session_id,))
            session['state_count'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM transcriptions WHERE session_id = ?', 
                          (session_id,))
            session['transcription_count'] = cursor.fetchone()[0]
            
            return session
        except Exception as e:
            print(f"Error getting session summary: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class SessionManager:
    """High-level session management"""
    
    def __init__(self, base_path: str = "./.session"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db = MemoryDatabase(str(self.base_path / "memory.db"))
        self.current_session_id: Optional[str] = None
    
    def start_session(self, blender_version: str = "4.5", 
                     project_name: str = "") -> str:
        """Start a new session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
        
        # Create session directory structure
        session_dir = self.base_path / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "audio").mkdir(exist_ok=True)
        (session_dir / "frames").mkdir(exist_ok=True)
        (session_dir / "embeddings").mkdir(exist_ok=True)
        (session_dir / "blender_state").mkdir(exist_ok=True)
        
        # Create metadata file
        metadata = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'blender_version': blender_version,
            'project_name': project_name,
            'windows_version': '10+',
        }
        
        with open(session_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Initialize database
        self.db.create_session(session_id, blender_version, project_name, metadata)
        self.current_session_id = session_id
        
        return session_id
    
    def log_event(self, event_type: str, data: Dict) -> bool:
        """Log an event to current session"""
        if not self.current_session_id:
            return False
        return self.db.add_timeline_event(self.current_session_id, event_type, data)
    
    def save_blender_state(self, state_data: Dict) -> bool:
        """Save Blender state to current session"""
        if not self.current_session_id:
            return False
        
        # Save to database
        self.db.save_blender_state(self.current_session_id, state_data)
        
        # Also save to file
        state_file = self.base_path / self.current_session_id / "blender_state" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        return True
    
    def end_session(self) -> bool:
        """End current session"""
        if not self.current_session_id:
            return False
        
        # Update session end time
        metadata_file = self.base_path / self.current_session_id / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['ended_at'] = datetime.now().isoformat()
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        self.current_session_id = None
        return True
    
    def get_current_session_id(self) -> Optional[str]:
        """Get current session ID"""
        return self.current_session_id
    
    def cleanup(self):
        """Cleanup resources"""
        self.db.close()
