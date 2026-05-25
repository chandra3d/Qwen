"""
Keyboard Hook Service
Tracks keyboard input and detects shortcuts
"""

from typing import Dict, List, Callable, Optional
from datetime import datetime
import threading
import time


class KeyboardHookService:
    """Global keyboard hook for tracking input"""
    
    def __init__(self):
        self.initialized = False
        self.is_listening = False
        self.callback: Optional[Callable[[Dict], None]] = None
        self.current_modifiers: List[str] = []
        self.key_history: List[Dict] = []
        self.max_history = 50
        
        # Key mapping for Blender shortcuts
        self.key_map = {
            13: 'Enter',
            27: 'Escape',
            9: 'Tab',
            32: 'Space',
            46: 'Delete',
            8: 'Backspace',
        }
        
        # Modifier keys
        self.modifier_keys = {
            160: 'Shift', 161: 'Shift',  # Left/Right Shift
            162: 'Ctrl', 163: 'Ctrl',    # Left/Right Ctrl
            164: 'Alt', 165: 'Alt',      # Left/Right Alt
            166: 'AltGr',                # Alt Gr
        }
    
    def initialize(self):
        """Initialize keyboard hook"""
        try:
            import keyboard
            self.initialized = True
            print("✓ Keyboard hook initialized")
            return True
        except Exception as e:
            print(f"Failed to initialize keyboard hook: {e}")
            print("  Note: May require admin privileges on Windows")
            return False
    
    def start_listening(self, callback: Callable[[Dict], None]):
        """Start listening for keyboard events"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.is_listening = True
        self.callback = callback
        
        try:
            import keyboard
            
            def on_event(event):
                if not self.is_listening:
                    return
                
                key_data = self._process_key_event(event)
                
                if key_data and self.callback:
                    self.callback(key_data)
                
                # Store in history
                self.key_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'data': key_data
                })
                
                # Trim history
                if len(self.key_history) > self.max_history:
                    self.key_history.pop(0)
            
            # Hook all keyboard events
            keyboard.hook(on_event)
            
        except Exception as e:
            print(f"Keyboard hook error: {e}")
            return False
        
        return True
    
    def stop_listening(self):
        """Stop listening for keyboard events"""
        self.is_listening = False
        
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
    
    def _process_key_event(self, event) -> Optional[Dict]:
        """Process raw keyboard event"""
        try:
            import keyboard
            
            key_name = event.name
            is_press = event.event_type == 'down'
            
            # Check if modifier key
            scan_code = event.scan_code
            
            if scan_code in self.modifier_keys:
                modifier = self.modifier_keys[scan_code]
                if is_press:
                    if modifier not in self.current_modifiers:
                        self.current_modifiers.append(modifier)
                else:
                    if modifier in self.current_modifiers:
                        self.current_modifiers.remove(modifier)
                return None  # Don't report modifier events alone
            
            # Get key name
            if scan_code in self.key_map:
                key_name = self.key_map[scan_code]
            elif hasattr(event, 'name') and event.name:
                key_name = event.name
            else:
                key_name = f'Key_{scan_code}'
            
            return {
                'key': key_name,
                'modifiers': self.current_modifiers.copy(),
                'is_press': is_press,
                'scan_code': scan_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Event processing error: {e}")
            return None
    
    def detect_shortcut(self, timeout: float = 0.5) -> Optional[str]:
        """Detect key combination (shortcut)"""
        if not self.current_modifiers:
            return None
        
        # Wait briefly for additional key press
        time.sleep(timeout)
        
        # This would need more sophisticated logic for real shortcut detection
        return None
    
    def get_recent_keys(self, count: int = 10) -> List[Dict]:
        """Get recent keyboard events"""
        return self.key_history[-count:]
    
    def get_active_modifiers(self) -> List[str]:
        """Get currently pressed modifier keys"""
        return self.current_modifiers.copy()
    
    def simulate_key_press(self, key: str):
        """Simulate a key press (for AI actions)"""
        try:
            import keyboard
            keyboard.press_and_release(key)
        except Exception as e:
            print(f"Key simulation error: {e}")
    
    def simulate_shortcut(self, modifiers: List[str], key: str):
        """Simulate a keyboard shortcut"""
        try:
            import keyboard
            
            # Press modifiers
            for mod in modifiers:
                keyboard.press(mod.lower())
            
            # Press and release main key
            keyboard.press_and_release(key.lower())
            
            # Release modifiers in reverse order
            for mod in reversed(modifiers):
                keyboard.release(mod.lower())
                
        except Exception as e:
            print(f"Shortcut simulation error: {e}")
