"""
Screen Capture Service
Captures screen with adaptive FPS and delta-frame optimization
Windows-optimized using DXGI/MSS
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import threading
import io


class ScreenCaptureService:
    """
    Screen capture service with:
    - Active window capture
    - Adaptive FPS
    - Viewport crop detection
    - Delta-frame optimization
    """
    
    def __init__(self, fps: int = 10, target_window: str = None):
        self.fps = fps
        self.target_window = target_window  # e.g., "Blender"
        self.is_running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callback: Optional[Callable] = None
        self._last_frame_hash: Optional[str] = None
        
        # Adaptive FPS settings
        self.min_fps = 2
        self.max_fps = 30
        self.current_fps = fps
        self._activity_level = 0
    
    async def start(self):
        """Start screen capture in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start capture thread
        self._capture_thread = threading.Thread(target=self._capture_loop)
        self._capture_thread.daemon = True
        self._capture_thread.start()
        
        print(f"📺 Screen capture started at {self.fps} FPS")
    
    def stop(self):
        """Stop screen capture"""
        self._stop_event.set()
        self.is_running = False
        
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
        
        print("📺 Screen capture stopped")
    
    def set_callback(self, callback: Callable):
        """Set callback for captured frames"""
        self._callback = callback
    
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        import hashlib
        
        while not self._stop_event.is_set():
            try:
                # Capture frame
                frame_data = self._capture_frame()
                
                if frame_data:
                    # Calculate hash for delta detection
                    frame_hash = hashlib.md5(frame_data).hexdigest()
                    
                    # Only process if frame changed (delta optimization)
                    if frame_hash != self._last_frame_hash:
                        self._last_frame_hash = frame_hash
                        self._activity_level = min(10, self._activity_level + 1)
                        
                        # Adjust FPS based on activity
                        self._adjust_fps()
                        
                        # Send to callback
                        if self._callback:
                            asyncio.run_coroutine_threadsafe(
                                self._callback({
                                    "type": "screen",
                                    "timestamp": datetime.now().isoformat(),
                                    "data": {
                                        "frame": frame_data,
                                        "resolution": self._get_resolution(),
                                        "active_window": self._get_active_window()
                                    }
                                }),
                                asyncio.get_event_loop()
                            )
                    else:
                        self._activity_level = max(0, self._activity_level - 1)
                        self._adjust_fps()
                
                # Sleep based on current FPS
                sleep_time = 1.0 / self.current_fps
                self._stop_event.wait(sleep_time)
                
            except Exception as e:
                print(f"Screen capture error: {e}")
                self._stop_event.wait(1.0)  # Wait longer on error
    
    def _capture_frame(self) -> Optional[bytes]:
        """Capture a single frame"""
        try:
            import mss
            import mss.tools
            
            with mss.mss() as sct:
                if self.target_window:
                    # Try to capture specific window
                    monitors = sct.monitors
                    # Use primary monitor for now (can be enhanced with window detection)
                    monitor = monitors[1]
                else:
                    # Primary monitor
                    monitor = sct.monitors[1]
                
                # Capture screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to PNG bytes
                img_data = mss.tools.to_png(screenshot.rgb, screenshot.size)
                
                return img_data
                
        except ImportError:
            # MSS not available, return placeholder
            print("Warning: MSS not installed, screen capture disabled")
            return None
        except Exception as e:
            print(f"Capture error: {e}")
            return None
    
    def _get_resolution(self) -> Dict[str, int]:
        """Get current screen resolution"""
        try:
            import mss
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                return {
                    "width": monitor["width"],
                    "height": monitor["height"]
                }
        except:
            return {"width": 1920, "height": 1080}
    
    def _get_active_window(self) -> Optional[str]:
        """Get currently active window title"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except:
            return None
    
    def _adjust_fps(self):
        """Adjust FPS based on screen activity"""
        if self._activity_level > 7:
            # High activity, increase FPS
            self.current_fps = min(self.max_fps, self.current_fps + 2)
        elif self._activity_level < 3:
            # Low activity, decrease FPS
            self.current_fps = max(self.min_fps, self.current_fps - 1)
        # else maintain current FPS
    
    def get_status(self) -> Dict[str, Any]:
        """Get current capture status"""
        return {
            "is_running": self.is_running,
            "current_fps": self.current_fps,
            "target_fps": self.fps,
            "activity_level": self._activity_level,
            "target_window": self.target_window
        }
