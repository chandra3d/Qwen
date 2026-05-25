"""
Mouse Tracking Service
Tracks mouse position, clicks, and gestures
"""

from typing import Dict, List, Callable, Optional, Tuple
from datetime import datetime
import threading
import time


class MouseTrackingService:
    """Global mouse tracking service"""
    
    def __init__(self):
        self.initialized = False
        self.is_tracking = False
        self.callback: Optional[Callable[[Dict], None]] = None
        self.position_history: List[Dict] = []
        self.click_history: List[Dict] = []
        self.max_history = 50
        
        # Current state
        self.current_x = 0
        self.current_y = 0
        self.buttons_pressed: List[str] = []
        
        # Gesture detection
        self.drag_start: Optional[Tuple[int, int]] = None
        self.is_dragging = False
    
    def initialize(self):
        """Initialize mouse tracking"""
        try:
            import mouse
            self.initialized = True
            print("✓ Mouse tracking initialized")
            return True
        except Exception as e:
            print(f"Failed to initialize mouse tracking: {e}")
            return False
    
    def start_tracking(self, callback: Callable[[Dict], None]):
        """Start tracking mouse events"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.is_tracking = True
        self.callback = callback
        
        try:
            import mouse
            
            def on_click(event):
                if not self.is_tracking:
                    return
                
                button = str(event.button)
                is_pressed = event.event_type == 'down'
                
                if is_pressed:
                    if button not in self.buttons_pressed:
                        self.buttons_pressed.append(button)
                    self.drag_start = (self.current_x, self.current_y)
                else:
                    if button in self.buttons_pressed:
                        self.buttons_pressed.remove(button)
                    self.drag_start = None
                
                click_data = {
                    'button': button,
                    'is_press': is_pressed,
                    'x': self.current_x,
                    'y': self.current_y,
                    'modifiers': [],  # Would need keyboard integration
                    'timestamp': datetime.now().isoformat()
                }
                
                self.click_history.append(click_data)
                if len(self.click_history) > self.max_history:
                    self.click_history.pop(0)
                
                if self.callback:
                    self.callback({
                        'type': 'click',
                        'data': click_data
                    })
            
            def on_move(event):
                if not self.is_tracking:
                    return
                
                self.current_x = event.x
                self.current_y = event.y
                
                move_data = {
                    'x': self.current_x,
                    'y': self.current_y,
                    'dx': event.x - (self.position_history[-1]['x'] if self.position_history else event.x),
                    'dy': event.y - (self.position_history[-1]['y'] if self.position_history else event.y),
                    'buttons_pressed': self.buttons_pressed.copy(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Check for drag
                if self.drag_start and len(self.buttons_pressed) > 0:
                    self.is_dragging = True
                    move_data['is_drag'] = True
                    move_data['drag_start'] = self.drag_start
                else:
                    self.is_dragging = False
                
                self.position_history.append(move_data)
                if len(self.position_history) > self.max_history:
                    self.position_history.pop(0)
                
                if self.callback:
                    self.callback({
                        'type': 'move',
                        'data': move_data
                    })
            
            def on_wheel(event):
                if not self.is_tracking:
                    return
                
                wheel_data = {
                    'delta': event.delta,
                    'x': self.current_x,
                    'y': self.current_y,
                    'timestamp': datetime.now().isoformat()
                }
                
                if self.callback:
                    self.callback({
                        'type': 'wheel',
                        'data': wheel_data
                    })
            
            # Hook mouse events
            mouse.on_click(on_click)
            mouse.on_move(on_move)
            mouse.on_wheel(on_wheel)
            
        except Exception as e:
            print(f"Mouse tracking error: {e}")
            return False
        
        return True
    
    def stop_tracking(self):
        """Stop tracking mouse events"""
        self.is_tracking = False
        
        try:
            import mouse
            mouse.unhook_all()
        except:
            pass
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        try:
            import mouse
            pos = mouse.get_position()
            self.current_x = pos[0]
            self.current_y = pos[1]
            return pos
        except:
            return (self.current_x, self.current_y)
    
    def move_to(self, x: int, y: int, duration: float = 0.1):
        """Move mouse to position"""
        try:
            import mouse
            mouse.move(x, y, duration=duration)
        except Exception as e:
            print(f"Mouse move error: {e}")
    
    def click(self, button: str = 'left'):
        """Simulate mouse click"""
        try:
            import mouse
            if button == 'left':
                mouse.click()
            elif button == 'right':
                mouse.right_click()
            elif button == 'middle':
                mouse.middle_click()
        except Exception as e:
            print(f"Mouse click error: {e}")
    
    def double_click(self):
        """Simulate double click"""
        try:
            import mouse
            mouse.double_click()
        except Exception as e:
            print(f"Double click error: {e}")
    
    def scroll(self, amount: int, x: int = None, y: int = None):
        """Simulate scroll"""
        try:
            import mouse
            if x is not None and y is not None:
                mouse.move(x, y)
            mouse.wheel(amount)
        except Exception as e:
            print(f"Scroll error: {e}")
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             button: str = 'left', duration: float = 0.3):
        """Simulate drag operation"""
        try:
            import mouse
            mouse.move(start_x, start_y)
            mouse.press(button=button)
            mouse.move(end_x, end_y, duration=duration)
            mouse.release(button=button)
        except Exception as e:
            print(f"Drag error: {e}")
    
    def get_recent_positions(self, count: int = 10) -> List[Dict]:
        """Get recent mouse positions"""
        return self.position_history[-count:]
    
    def get_recent_clicks(self, count: int = 10) -> List[Dict]:
        """Get recent click events"""
        return self.click_history[-count:]
    
    def detect_gesture(self) -> Optional[str]:
        """Detect mouse gesture from recent movement"""
        if len(self.position_history) < 5:
            return None
        
        # Simple gesture detection
        recent = self.position_history[-10:]
        
        total_dx = sum(p['dx'] for p in recent)
        total_dy = sum(p['dy'] for p in recent)
        
        if abs(total_dx) > abs(total_dy) * 2:
            return 'swipe_right' if total_dx > 0 else 'swipe_left'
        elif abs(total_dy) > abs(total_dx) * 2:
            return 'swipe_down' if total_dy > 0 else 'swipe_up'
        
        return None
    
    def get_stats(self) -> Dict:
        """Get tracking statistics"""
        return {
            'initialized': self.initialized,
            'is_tracking': self.is_tracking,
            'current_position': (self.current_x, self.current_y),
            'buttons_pressed': self.buttons_pressed.copy(),
            'is_dragging': self.is_dragging,
            'position_history_size': len(self.position_history),
            'click_history_size': len(self.click_history)
        }
