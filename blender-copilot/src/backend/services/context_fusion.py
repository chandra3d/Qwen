"""
Context Fusion Engine
Combines multiple input streams into semantic context
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid


class ContextFusionEngine:
    """
    Fuses screen, keyboard, mouse, voice, and Blender state
    into a unified semantic context for AI understanding
    """
    
    def __init__(self):
        self.current_context: Dict[str, Any] = {}
        self.context_history: List[Dict] = []
        self.session_id: Optional[str] = None
        self._lock = asyncio.Lock()
        
        # Input buffers
        self.screen_buffer: List[Dict] = []
        self.keyboard_buffer: List[Dict] = []
        self.mouse_buffer: List[Dict] = []
        self.voice_buffer: List[Dict] = []
        self.blender_buffer: List[Dict] = []
        
        # Configuration
        self.max_buffer_size = 100
        self.context_window_seconds = 60  # Keep last 60 seconds of context
    
    async def process_data(self, data: Dict) -> Dict:
        """Process incoming multimodal data"""
        async with self._lock:
            data_type = data.get("type")
            timestamp = data.get("timestamp", datetime.now().isoformat())
            
            if data_type == "screen":
                self.screen_buffer.append(data)
                self._trim_buffer(self.screen_buffer)
            elif data_type == "keyboard":
                self.keyboard_buffer.append(data)
                self._trim_buffer(self.keyboard_buffer)
            elif data_type == "mouse":
                self.mouse_buffer.append(data)
                self._trim_buffer(self.mouse_buffer)
            elif data_type == "voice":
                self.voice_buffer.append(data)
                self._trim_buffer(self.voice_buffer)
            elif data_type == "blender_state":
                self.blender_buffer.append(data)
                self._trim_buffer(self.blender_buffer)
            
            # Fuse all inputs into current context
            self.current_context = await self._fuse_contexts(timestamp)
            
            # Add to history
            self.context_history.append({
                "id": str(uuid.uuid4()),
                "timestamp": timestamp,
                "context": self.current_context.copy()
            })
            
            return self.current_context
    
    async def add_blender_state(self, blender_state: Dict):
        """Add Blender state to the fusion engine"""
        blender_state["type"] = "blender_state"
        blender_state["timestamp"] = datetime.now().isoformat()
        await self.process_data(blender_state)
    
    async def _fuse_contexts(self, timestamp: str) -> Dict:
        """Fuse all input buffers into a single semantic context"""
        
        # Get latest from each buffer
        latest_screen = self.screen_buffer[-1] if self.screen_buffer else None
        latest_keyboard = self.keyboard_buffer[-1] if self.keyboard_buffer else None
        latest_mouse = self.mouse_buffer[-1] if self.mouse_buffer else None
        latest_voice = self.voice_buffer[-1] if self.voice_buffer else None
        latest_blender = self.blender_buffer[-1] if self.blender_buffer else None
        
        # Extract recent activity (last N events)
        recent_keyboard = self.keyboard_buffer[-10:] if len(self.keyboard_buffer) > 10 else self.keyboard_buffer
        recent_mouse = self.mouse_buffer[-10:] if len(self.mouse_buffer) > 10 else self.mouse_buffer
        recent_voice = self.voice_buffer[-5:] if len(self.voice_buffer) > 5 else self.voice_buffer
        
        # Detect intent from keyboard shortcuts
        detected_shortcuts = self._detect_shortcuts(recent_keyboard)
        detected_actions = self._detect_actions(detected_shortcuts, latest_blender)
        
        # Build fused context
        fused = {
            "id": str(uuid.uuid4()),
            "timestamp": timestamp,
            "session_id": self.session_id,
            
            # Current state
            "blender_state": latest_blender.get("data") if latest_blender else None,
            "screen_info": latest_screen.get("data") if latest_screen else None,
            
            # Recent activity
            "recent_actions": detected_actions,
            "recent_shortcuts": detected_shortcuts,
            "recent_voice_commands": [v.get("transcription") for v in recent_voice if v.get("transcription")],
            
            # Mouse & interaction
            "mouse_activity": {
                "position": latest_mouse.get("data", {}).get("position") if latest_mouse else None,
                "clicks": len([m for m in recent_mouse if m.get("data", {}).get("clicked")])
            },
            
            # Semantic interpretation
            "inferred_intent": self._infer_intent(detected_actions, recent_voice),
            "workflow_stage": self._detect_workflow_stage(latest_blender),
            
            # Metadata
            "confidence_score": self._calculate_confidence(),
            "input_sources": {
                "screen": len(self.screen_buffer) > 0,
                "keyboard": len(self.keyboard_buffer) > 0,
                "mouse": len(self.mouse_buffer) > 0,
                "voice": len(self.voice_buffer) > 0,
                "blender": len(self.blender_buffer) > 0
            }
        }
        
        return fused
    
    def _detect_shortcuts(self, keyboard_events: List[Dict]) -> List[Dict]:
        """Detect keyboard shortcuts from key events"""
        shortcuts = []
        
        # Common Blender shortcuts
        shortcut_map = {
            ("ctrl", "r"): "loop_cut",
            ("ctrl", "b"): "bevel",
            ("e",): "extrude",
            ("g",): "grab_move",
            ("r",): "rotate",
            ("s",): "scale",
            ("ctrl", "z"): "undo",
            ("ctrl", "shift", "z"): "redo",
            ("tab",): "toggle_edit_mode",
            ("delete",): "delete_object",
            ("x",): "delete_menu",
            ("shift", "a"): "add_menu",
            ("n",): "toggle_sidebar",
            ("t",): "toggle_toolbar",
        }
        
        # Simple detection (can be enhanced with timing analysis)
        recent_keys = [k.get("key", "").lower() for k in keyboard_events[-5:]]
        
        for keys, action in shortcut_map.items():
            if all(key in recent_keys for key in keys):
                shortcuts.append({
                    "keys": list(keys),
                    "action": action,
                    "timestamp": datetime.now().isoformat()
                })
        
        return shortcuts
    
    def _detect_actions(self, shortcuts: List[Dict], blender_state: Optional[Dict]) -> List[Dict]:
        """Detect higher-level actions from shortcuts and Blender state"""
        actions = []
        
        for shortcut in shortcuts:
            action = shortcut.get("action")
            if blender_state and blender_state.get("data"):
                actions.append({
                    "action": action,
                    "context": blender_state["data"].get("active_object"),
                    "mode": blender_state["data"].get("active_mode"),
                    "timestamp": shortcut.get("timestamp")
                })
            else:
                actions.append({
                    "action": action,
                    "context": None,
                    "mode": None,
                    "timestamp": shortcut.get("timestamp")
                })
        
        return actions
    
    def _infer_intent(self, actions: List[Dict], voice_commands: List[Dict]) -> Optional[str]:
        """Infer user intent from actions and voice commands"""
        if not actions and not voice_commands:
            return None
        
        # Simple intent inference (can be enhanced with ML model)
        modeling_actions = ["loop_cut", "bevel", "extrude", "grab_move", "rotate", "scale"]
        navigation_actions = ["grab_move", "rotate"]  # View navigation
        
        action_types = [a.get("action") for a in actions]
        
        if any(action in modeling_actions for action in action_types):
            return "modeling"
        elif voice_commands:
            return "voice_command"
        elif len(actions) > 3:
            return "active_work"
        else:
            return "general"
    
    def _detect_workflow_stage(self, blender_state: Optional[Dict]) -> str:
        """Detect current workflow stage from Blender state"""
        if not blender_state or not blender_state.get("data"):
            return "unknown"
        
        data = blender_state["data"]
        mode = data.get("active_mode", "OBJECT")
        
        stage_map = {
            "OBJECT": "object_management",
            "EDIT": "mesh_editing",
            "SCULPT": "sculpting",
            "PAINT_VERTEX": "vertex_painting",
            "PAINT_TEXTURE": "texture_painting",
            "WEIGHT_PAINT": "weight_painting",
            "POSE": "posing",
            "NODE_EDIT": "node_editing",
            "TEXTURE": "texture_setup"
        }
        
        return stage_map.get(mode, "general")
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score based on available input sources"""
        active_sources = sum([
            len(self.screen_buffer) > 0,
            len(self.keyboard_buffer) > 0,
            len(self.mouse_buffer) > 0,
            len(self.voice_buffer) > 0,
            len(self.blender_buffer) > 0
        ])
        
        # Confidence increases with more input sources
        return min(1.0, active_sources / 3.0)
    
    def _trim_buffer(self, buffer: List, max_size: int = None):
        """Trim buffer to maximum size"""
        if max_size is None:
            max_size = self.max_buffer_size
        
        while len(buffer) > max_size:
            buffer.pop(0)
    
    def get_current_context(self) -> Dict:
        """Get the current fused context"""
        return self.current_context.copy()
    
    async def shutdown(self):
        """Cleanup resources"""
        self.screen_buffer.clear()
        self.keyboard_buffer.clear()
        self.mouse_buffer.clear()
        self.voice_buffer.clear()
        self.blender_buffer.clear()
        self.context_history.clear()
