"""
Screen Capture Service
Captures screen frames with adaptive FPS
"""

import numpy as np
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import time


class ScreenCaptureService:
    """Screen capture service using MSS (fast cross-platform)"""
    
    def __init__(self):
        self.initialized = False
        self.sct = None
        self.monitor = None
        self.is_capturing = False
        self.fps = 1.0
        self.adaptive_fps = True
        self.callback: Optional[Callable] = None
        
        # Performance tracking
        self.last_capture_time = 0
        self.frame_count = 0
    
    def initialize(self, monitor_id: int = 1):
        """Initialize screen capture"""
        try:
            import mss
            self.sct = mss.mss()
            
            # Get monitor info
            monitors = self.sct.monitors
            if monitor_id < len(monitors):
                self.monitor = monitors[monitor_id]
            else:
                self.monitor = monitors[1]  # Default to first monitor
            
            self.initialized = True
            print(f"✓ Screen capture initialized: {self.monitor['width']}x{self.monitor['height']}")
            return True
        except Exception as e:
            print(f"Failed to initialize screen capture: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame"""
        if not self.initialized:
            if not self.initialize():
                return None
        
        try:
            start_time = time.time()
            
            # Capture screen
            screenshot = self.sct.grab(self.monitor)
            
            # Convert to numpy array (BGR format)
            frame = np.array(screenshot)
            
            # Update performance metrics
            capture_time = time.time() - start_time
            self.last_capture_time = capture_time
            self.frame_count += 1
            
            # Adaptive FPS adjustment
            if self.adaptive_fps:
                self._adjust_fps(capture_time)
            
            return frame
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
    
    def capture_to_bytes(self) -> Optional[bytes]:
        """Capture frame and return as PNG bytes"""
        frame = self.capture_frame()
        
        if frame is None:
            return None
        
        try:
            from PIL import Image
            import io
            
            # Convert numpy array to PIL Image
            image = Image.fromarray(frame)
            
            # Save to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            
            return buffer.getvalue()
        except Exception as e:
            print(f"Frame conversion error: {e}")
            return None
    
    def _adjust_fps(self, capture_time: float):
        """Adjust FPS based on capture performance"""
        # Target ~33ms per frame (30 FPS) for smooth capture
        target_time = 0.033
        
        if capture_time > target_time * 2:
            # Slow down if capture is too slow
            self.fps = max(0.5, self.fps * 0.8)
        elif capture_time < target_time * 0.5:
            # Speed up if capture is fast
            self.fps = min(10.0, self.fps * 1.1)
    
    def start_continuous_capture(self, callback: Callable[[np.ndarray], None], 
                                  fps: float = 1.0):
        """Start continuous screen capture"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.is_capturing = True
        self.callback = callback
        self.fps = fps
        
        import threading
        
        def capture_loop():
            interval = 1.0 / fps
            
            while self.is_capturing:
                start_time = time.time()
                
                frame = self.capture_frame()
                if frame is not None and self.callback:
                    self.callback(frame)
                
                # Sleep to maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
        
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
        
        return True
    
    def stop_continuous_capture(self):
        """Stop continuous capture"""
        self.is_capturing = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=2.0)
    
    def get_capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """Capture specific region of screen"""
        if not self.initialized:
            if not self.initialize():
                return None
        
        try:
            monitor = {
                'left': x,
                'top': y,
                'width': width,
                'height': height
            }
            
            screenshot = self.sct.grab(monitor)
            frame = np.array(screenshot)
            
            return frame
        except Exception as e:
            print(f"Region capture error: {e}")
            return None
    
    def detect_active_window(self) -> Optional[Dict[str, Any]]:
        """Detect currently active window (Windows only)"""
        try:
            import win32gui
            import win32process
            
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            
            return {
                'hwnd': hwnd,
                'pid': pid,
                'title': window_title,
                'class': window_class,
                'is_blender': 'Blender' in window_title
            }
        except Exception as e:
            # win32gui not available or error
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get capture statistics"""
        return {
            'initialized': self.initialized,
            'is_capturing': self.is_capturing,
            'current_fps': self.fps,
            'frame_count': self.frame_count,
            'last_capture_time_ms': self.last_capture_time * 1000,
            'monitor_resolution': f"{self.monitor['width']}x{self.monitor['height']}" if self.monitor else None
        }
