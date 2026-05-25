"""
Mouse Tracking Service
Tracks mouse position, clicks, and drag operations
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, List, Any
import threading


class MouseTrackingService:
    """
    Mouse tracking service with:
    - Position tracking
    - Click detection
    - Drag tracking
    - Viewport interaction mapping
    """
    
    def __init__(self, context_engine=None):
        self.context_engine = context_engine
        self.is_running = False
        self._hook_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._recent_events: List[Dict] = []
        self._max_recent_events = 50
        
        # Mouse state
        self._current_position = {"x": 0, "y": 0}
        self._is_dragging = False
        self._drag_start = None
        self._click_count = 0
        self._last_click_time = None
    
    def start(self):
        """Start mouse tracking in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start tracking thread
        self._hook_thread = threading.Thread(target=self._tracking_loop)
        self._hook_thread.daemon = True
        self._hook_thread.start()
        
        print("🖱️  Mouse tracking started")
    
    def stop(self):
        """Stop mouse tracking"""
        self._stop_event.set()
        self.is_running = False
        
        if self._hook_thread:
            self._hook_thread.join(timeout=2.0)
        
        print("🖱️  Mouse tracking stopped")
    
    def _tracking_loop(self):
        """Main tracking loop running in separate thread"""
        try:
            import pynput
            
            # Callback for mouse movement
            def on_move(x, y):
                if self._stop_event.is_set():
                    return
                
                self._process_move(x, y)
            
            # Callback for mouse clicks
            def on_click(x, y, button, pressed):
                if self._stop_event.is_set():
                    return
                
                self._process_click(x, y, button, pressed)
            
            # Callback for scroll
            def on_scroll(x, y, dx, dy):
                if self._stop_event.is_set():
                    return
                
                self._process_scroll(x, y, dx, dy)
            
            # Start listener
            with pynput.mouse.Listener(
                on_move=on_move,
                on_click=on_click,
                on_scroll=on_scroll
            ) as listener:
                while not self._stop_event.is_set():
                    self._stop_event.wait(0.1)
                
                listener.stop()
                
        except ImportError:
            print("Warning: pynput module not installed, mouse tracking disabled")
            self._stop_event.wait()
        except Exception as e:
            print(f"Mouse tracking error: {e}")
            self._stop_event.wait(1.0)
    
    def _process_move(self, x, y):
        """Process mouse movement"""
        try:
            self._current_position = {"x": int(x), "y": int(y)}
            
            # Create move event
            move_event = {
                "type": "move",
                "position": self._current_position.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to recent events
            self._recent_events.append(move_event)
            if len(self._recent_events) > self._max_recent_events:
                self._recent_events.pop(0)
            
            # Send to context engine (throttled)
            if self.context_engine and len(self._recent_events) % 10 == 0:
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self.context_engine.process_data({
                        "type": "mouse",
                        "subtype": "move",
                        "timestamp": move_event["timestamp"],
                        "data": move_event
                    }),
                    asyncio.get_event_loop()
                )
                
        except Exception as e:
            print(f"Error processing mouse move: {e}")
    
    def _process_click(self, x, y, button, pressed):
        """Process mouse click"""
        try:
            timestamp = datetime.now().isoformat()
            position = {"x": int(x), "y": int(y)}
            
            # Detect double-click
            is_double_click = False
            if pressed and self._last_click_time:
                time_diff = (datetime.now() - self._last_click_time).total_seconds()
                if time_diff < 0.3:  # 300ms threshold
                    is_double_click = True
            
            if pressed:
                self._last_click_time = datetime.now()
                self._click_count += 1
                self._drag_start = position.copy()
                self._is_dragging = False
            else:
                # Check if it was a drag
                if self._drag_start:
                    dx = abs(position["x"] - self._drag_start["x"])
                    dy = abs(position["y"] - self._drag_start["y"])
                    if dx > 5 or dy > 5:
                        self._is_dragging = True
            
            # Create click event
            click_event = {
                "type": "click" if pressed else "release",
                "position": position,
                "button": str(button),
                "is_pressed": pressed,
                "is_double_click": is_double_click,
                "is_drag": self._is_dragging if not pressed else False,
                "drag_start": self._drag_start.copy() if self._drag_start else None,
                "timestamp": timestamp
            }
            
            # Add to recent events
            self._recent_events.append(click_event)
            if len(self._recent_events) > self._max_recent_events:
                self._recent_events.pop(0)
            
            # Send to context engine
            if self.context_engine:
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self.context_engine.process_data({
                        "type": "mouse",
                        "subtype": "click" if pressed else "release",
                        "timestamp": timestamp,
                        "data": click_event
                    }),
                    asyncio.get_event_loop()
                )
            
            # Reset drag state on release
            if not pressed:
                self._drag_start = None
                self._is_dragging = False
                
        except Exception as e:
            print(f"Error processing mouse click: {e}")
    
    def _process_scroll(self, x, y, dx, dy):
        """Process mouse scroll"""
        try:
            scroll_event = {
                "type": "scroll",
                "position": {"x": int(x), "y": int(y)},
                "delta": {"dx": int(dx), "dy": int(dy)},
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to recent events
            self._recent_events.append(scroll_event)
            if len(self._recent_events) > self._max_recent_events:
                self._recent_events.pop(0)
            
            # Send to context engine
            if self.context_engine:
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self.context_engine.process_data({
                        "type": "mouse",
                        "subtype": "scroll",
                        "timestamp": scroll_event["timestamp"],
                        "data": scroll_event
                    }),
                    asyncio.get_event_loop()
                )
                
        except Exception as e:
            print(f"Error processing mouse scroll: {e}")
    
    def get_current_position(self) -> Dict[str, int]:
        """Get current mouse position"""
        return self._current_position.copy()
    
    def get_recent_events(self) -> List[Dict]:
        """Get recent mouse events"""
        return self._recent_events.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current tracking status"""
        return {
            "is_running": self.is_running,
            "current_position": self._current_position,
            "recent_events_count": len(self._recent_events),
            "is_dragging": self._is_dragging,
            "click_count": self._click_count
        }
