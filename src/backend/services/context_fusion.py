"""
Context Fusion Engine
Combines multiple input streams into unified semantic context
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime


class ContextFusionEngine:
    """Fuses screen, keyboard, mouse, voice, and Blender state into context"""
    
    def __init__(self):
        self.context_buffer: Dict[str, List[Dict]] = {}
        self.current_context: Dict[str, Any] = {}
        self.blender_state: Dict[str, Any] = {}
        self.voice_history: List[Dict] = []
        self.keyboard_sequence: List[Dict] = []
        self.mouse_events: List[Dict] = []
        self.screen_frames: List[Dict] = []
        
        # Configuration
        self.max_buffer_size = 100
        self.sequence_window = 10  # Last N events for pattern detection
    
    async def shutdown(self):
        """Cleanup resources"""
        self.context_buffer.clear()
        self.current_context.clear()
    
    def process_keyboard_event(self, session_id: str, data: Dict):
        """Process keyboard event"""
        if session_id not in self.context_buffer:
            self.context_buffer[session_id] = []
        
        event = {
            'type': 'keyboard',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.keyboard_sequence.append(event)
        if len(self.keyboard_sequence) > self.sequence_window:
            self.keyboard_sequence.pop(0)
        
        # Detect shortcuts
        shortcut = self._detect_shortcut(data)
        if shortcut:
            event['shortcut'] = shortcut
            event['intent'] = self._map_shortcut_to_intent(shortcut)
        
        self.context_buffer[session_id].append(event)
        self._trim_buffer(session_id)
    
    def process_mouse_event(self, session_id: str, data: Dict):
        """Process mouse event"""
        if session_id not in self.context_buffer:
            self.context_buffer[session_id] = []
        
        event = {
            'type': 'mouse',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.mouse_events.append(event)
        if len(self.mouse_events) > self.sequence_window:
            self.mouse_events.pop(0)
        
        self.context_buffer[session_id].append(event)
        self._trim_buffer(session_id)
    
    def process_voice_event(self, session_id: str, data: Dict):
        """Process voice transcription event"""
        if session_id not in self.context_buffer:
            self.context_buffer[session_id] = []
        
        event = {
            'type': 'voice',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.voice_history.append(event)
        if len(self.voice_history) > self.sequence_window:
            self.voice_history.pop(0)
        
        self.context_buffer[session_id].append(event)
        self._trim_buffer(session_id)
    
    def process_screen_event(self, session_id: str, data: Dict):
        """Process screen capture event"""
        if session_id not in self.context_buffer:
            self.context_buffer[session_id] = []
        
        event = {
            'type': 'screen',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.screen_frames.append(event)
        if len(self.screen_frames) > self.sequence_window:
            self.screen_frames.pop(0)
        
        self.context_buffer[session_id].append(event)
        self._trim_buffer(session_id)
    
    def update_blender_state(self, state: Dict):
        """Update current Blender state"""
        self.blender_state = {
            **self.blender_state,
            **state,
            'updated_at': datetime.now().isoformat()
        }
    
    def _detect_shortcut(self, keyboard_data: Dict) -> Optional[str]:
        """Detect keyboard shortcuts from key event"""
        modifiers = keyboard_data.get('modifiers', [])
        key = keyboard_data.get('key', '')
        
        if not key:
            return None
        
        # Build shortcut string
        modifier_str = '+'.join(sorted(modifiers)) if modifiers else ''
        shortcut = f"{modifier_str}+{key}" if modifier_str else key
        
        # Common Blender shortcuts
        blender_shortcuts = {
            'Ctrl+R': 'Loop Cut',
            'E': 'Extrude',
            'G': 'Grab/Move',
            'R': 'Rotate',
            'S': 'Scale',
            'Ctrl+Z': 'Undo',
            'Ctrl+Shift+Z': 'Redo',
            'X': 'Delete',
            'Shift+A': 'Add',
            'Tab': 'Toggle Edit Mode',
            'Ctrl+J': 'Join Objects',
            'Ctrl+P': 'Parent',
            'Alt+H': 'Unhide All',
        }
        
        return blender_shortcuts.get(shortcut)
    
    def _map_shortcut_to_intent(self, shortcut: str) -> str:
        """Map shortcut to user intent"""
        intent_map = {
            'Loop Cut': 'modeling_edit',
            'Extrude': 'modeling_create',
            'Grab/Move': 'transform_move',
            'Rotate': 'transform_rotate',
            'Scale': 'transform_scale',
            'Undo': 'edit_undo',
            'Redo': 'edit_redo',
            'Delete': 'object_remove',
            'Add': 'object_create',
            'Toggle Edit Mode': 'mode_switch',
            'Join Objects': 'object_combine',
            'Parent': 'object_hierarchy',
            'Unhide All': 'visibility_manage',
        }
        
        return intent_map.get(shortcut, 'general_action')
    
    def _trim_buffer(self, session_id: str):
        """Trim buffer to max size"""
        if len(self.context_buffer[session_id]) > self.max_buffer_size:
            self.context_buffer[session_id] = \
                self.context_buffer[session_id][-self.max_buffer_size:]
    
    def get_fused_context(self, session_id: str) -> Dict:
        """Get fused context for a session"""
        recent_events = self.context_buffer.get(session_id, [])[-20:]
        
        return {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'blender_state': self.blender_state,
            'recent_events': recent_events,
            'keyboard_sequence': self.keyboard_sequence[-5:],
            'mouse_events': self.mouse_events[-5:],
            'voice_history': self.voice_history[-5:],
            'detected_shortcuts': [
                e.get('shortcut') for e in recent_events 
                if e.get('shortcut')
            ],
            'inferred_intent': self._infer_intent(recent_events)
        }
    
    def _infer_intent(self, events: List[Dict]) -> str:
        """Infer user intent from recent events"""
        if not events:
            return 'unknown'
        
        # Count event types
        event_types = [e['type'] for e in events[-10:]]
        
        # Check for modeling activity
        shortcuts = [e.get('shortcut') for e in events if e.get('shortcut')]
        modeling_shortcuts = ['Extrude', 'Loop Cut', 'Grab/Move', 'Rotate', 'Scale']
        
        if any(s in modeling_shortcuts for s in shortcuts):
            return 'modeling'
        
        # Check for voice-guided activity
        if event_types.count('voice') > 3:
            return 'voice_controlled'
        
        # Check for navigation
        if event_types.count('mouse') > 7:
            return 'navigating'
        
        return 'general_workflow'
    
    async def generate_response(self, query: str, session_id: str) -> Dict:
        """Generate AI response based on context"""
        context = self.get_fused_context(session_id)
        
        # Placeholder response - would integrate with LLM/VLM
        response = {
            'query': query,
            'context_summary': {
                'blender_mode': context['blender_state'].get('active_mode', 'Unknown'),
                'selected_objects': context['blender_state'].get('selected_objects', []),
                'recent_actions': context['detected_shortcuts'],
                'inferred_intent': context['inferred_intent']
            },
            'suggestion': self._generate_suggestion(query, context),
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def _generate_suggestion(self, query: str, context: Dict) -> str:
        """Generate contextual suggestion"""
        intent = context['inferred_intent']
        shortcuts = context['detected_shortcuts']
        
        if intent == 'modeling':
            return "You're in modeling mode. Consider using Ctrl+R for loop cuts or E for extrusion."
        
        if 'Undo' in shortcuts and len(shortcuts) > 2:
            return "Multiple undos detected. Would you like to try a different approach?"
        
        if not shortcuts:
            return "Start by selecting an object and pressing G to move, R to rotate, or S to scale."
        
        return "Continue your workflow. I'm monitoring your actions to provide assistance."
