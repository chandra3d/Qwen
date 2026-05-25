"""
Keyboard Hook Service
Global keyboard listener with shortcut detection for Blender
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, List, Any
import threading


class KeyboardHookService:
    """
    Global keyboard hook service with:
    - Shortcut detection
    - Key sequence understanding
    - Intent prediction
    """
    
    def __init__(self, context_engine=None):
        self.context_engine = context_engine
        self.is_running = False
        self._hook_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._recent_keys: List[Dict] = []
        self._max_recent_keys = 20
        
        # Modifier key states
        self._modifiers = {
            "ctrl": False,
            "shift": False,
            "alt": False,
            "win": False
        }
        
        # Known Blender shortcuts
        self.blender_shortcuts = {
            ("ctrl", "r"): {"action": "loop_cut", "description": "Add loop cut"},
            ("ctrl", "b"): {"action": "bevel", "description": "Bevel vertices/edges"},
            ("e",): {"action": "extrude", "description": "Extrude selection"},
            ("g",): {"action": "grab_move", "description": "Grab/Move"},
            ("r",): {"action": "rotate", "description": "Rotate"},
            ("s",): {"action": "scale", "description": "Scale"},
            ("ctrl", "z"): {"action": "undo", "description": "Undo"},
            ("ctrl", "shift", "z"): {"action": "redo", "description": "Redo"},
            ("tab",): {"action": "toggle_edit_mode", "description": "Toggle Edit/Object mode"},
            ("delete",): {"action": "delete_object", "description": "Delete"},
            ("x",): {"action": "delete_menu", "description": "Delete menu"},
            ("shift", "a"): {"action": "add_menu", "description": "Add menu"},
            ("n",): {"action": "toggle_sidebar", "description": "Toggle sidebar"},
            ("t",): {"action": "toggle_toolbar", "description": "Toggle toolbar"},
            ("ctrl", "j"): {"action": "join_meshes", "description": "Join meshes"},
            ("ctrl", "p"): {"action": "parent", "description": "Parent object"},
            ("alt", "p"): {"action": "clear_parent", "description": "Clear parent"},
            ("shift", "d"): {"action": "duplicate", "description": "Duplicate"},
            ("h",): {"action": "hide", "description": "Hide selection"},
            ("alt", "h"): {"action": "unhide_all", "description": "Unhide all"},
            ("z",): {"action": "shade_toggle", "description": "Toggle wireframe/solid"},
            ("shift", "z"): {"action": "wireframe_toggle", "description": "Toggle wireframe"},
        }
    
    def start(self):
        """Start keyboard hook in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start hook thread
        self._hook_thread = threading.Thread(target=self._hook_loop)
        self._hook_thread.daemon = True
        self._hook_thread.start()
        
        print("⌨️  Keyboard hook started")
    
    def stop(self):
        """Stop keyboard hook"""
        self._stop_event.set()
        self.is_running = False
        
        if self._hook_thread:
            self._hook_thread.join(timeout=2.0)
        
        print("⌨️  Keyboard hook stopped")
    
    def _hook_loop(self):
        """Main hook loop running in separate thread"""
        try:
            import keyboard
            
            # Define callback for key events
            def on_key_event(event):
                if self._stop_event.is_set():
                    return
                
                self._process_key_event(event)
            
            # Start listening
            keyboard.hook(on_key_event)
            
            # Wait until stop event
            while not self._stop_event.is_set():
                self._stop_event.wait(0.1)
            
            # Unhook
            keyboard.unhook_all()
            
        except ImportError:
            print("Warning: keyboard module not installed, keyboard hook disabled")
            self._stop_event.wait()
        except Exception as e:
            print(f"Keyboard hook error: {e}")
            self._stop_event.wait(1.0)
    
    def _process_key_event(self, event):
        """Process individual key event"""
        try:
            key_name = event.name.lower()
            is_pressed = event.event_type == 'down'
            
            # Track modifier keys
            if key_name in self._modifiers:
                self._modifiers[key_name] = is_pressed
            
            # Create key event record
            key_event = {
                "key": key_name,
                "is_pressed": is_pressed,
                "modifiers": self._get_active_modifiers(),
                "timestamp": datetime.now().isoformat(),
                "scan_code": event.scan_code
            }
            
            # Add to recent keys
            self._recent_keys.append(key_event)
            if len(self._recent_keys) > self._max_recent_keys:
                self._recent_keys.pop(0)
            
            # Detect shortcuts on key press
            if is_pressed:
                shortcut_info = self._detect_shortcut()
                
                if shortcut_info:
                    # Send to context engine
                    if self.context_engine:
                        import asyncio
                        asyncio.run_coroutine_threadsafe(
                            self.context_engine.process_data({
                                "type": "keyboard",
                                "subtype": "shortcut",
                                "timestamp": key_event["timestamp"],
                                "data": {
                                    "shortcut": shortcut_info,
                                    "key_event": key_event
                                }
                            }),
                            asyncio.get_event_loop()
                        )
                    else:
                        print(f"🎹 Shortcut detected: {shortcut_info['action']}")
            
            # Also send regular key events
            if self.context_engine:
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self.context_engine.process_data({
                        "type": "keyboard",
                        "subtype": "key",
                        "timestamp": key_event["timestamp"],
                        "data": key_event
                    }),
                    asyncio.get_event_loop()
                )
                
        except Exception as e:
            print(f"Error processing key event: {e}")
    
    def _get_active_modifiers(self) -> List[str]:
        """Get list of currently pressed modifier keys"""
        return [key for key, pressed in self._modifiers.items() if pressed]
    
    def _detect_shortcut(self) -> Optional[Dict]:
        """Detect if a known shortcut was pressed"""
        active_mods = self._get_active_modifiers()
        
        # Get the most recent non-modifier key
        recent_non_modifier = None
        for key_event in reversed(self._recent_keys):
            if key_event["key"] not in self._modifiers and key_event["is_pressed"]:
                recent_non_modifier = key_event["key"]
                break
        
        if not recent_non_modifier:
            return None
        
        # Build potential shortcut combinations
        potential_shortcuts = []
        
        # Single key
        potential_shortcuts.append((recent_non_modifier,))
        
        # With modifiers
        if active_mods:
            potential_shortcuts.append(tuple(active_mods + [recent_non_modifier]))
        
        # Check against known shortcuts
        for shortcut_tuple in potential_shortcuts:
            if shortcut_tuple in self.blender_shortcuts:
                shortcut_data = self.blender_shortcuts[shortcut_tuple]
                return {
                    "keys": list(shortcut_tuple),
                    "action": shortcut_data["action"],
                    "description": shortcut_data["description"],
                    "timestamp": datetime.now().isoformat()
                }
        
        return None
    
    def get_recent_keys(self) -> List[Dict]:
        """Get recent key events"""
        return self._recent_keys.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current hook status"""
        return {
            "is_running": self.is_running,
            "recent_keys_count": len(self._recent_keys),
            "active_modifiers": self._get_active_modifiers()
        }
