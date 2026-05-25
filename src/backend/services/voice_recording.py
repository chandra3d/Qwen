"""
Voice Recording Service
Records and transcribes voice using Faster-Whisper
"""

import numpy as np
from typing import Optional, Dict, Callable, List
from datetime import datetime
import threading
import time
import wave
import io


class VoiceRecordingService:
    """Voice recording and transcription service"""
    
    def __init__(self):
        self.initialized = False
        self.is_recording = False
        self.transcriber = None
        self.callback: Optional[Callable[[str], None]] = None
        self.audio_buffer: List[np.ndarray] = []
        self.recording_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.transcription_language = 'en'
        
        # Session storage
        self.current_session_id: Optional[str] = None
        self.audio_files: List[str] = []
    
    def initialize(self, model_size: str = "base"):
        """Initialize Whisper transcription model"""
        try:
            from faster_whisper import WhisperModel
            
            # Load model
            self.transcriber = WhisperModel(
                model_size, 
                device="cpu", 
                compute_type="int8"
            )
            
            self.initialized = True
            print(f"✓ Voice service initialized with {model_size} model")
            return True
        except Exception as e:
            print(f"Failed to initialize voice service: {e}")
            print("  Note: Install faster-whisper: pip install faster-whisper")
            return False
    
    def start_recording(self, callback: Optional[Callable[[str], None]] = None):
        """Start recording audio"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        self.is_recording = True
        self.callback = callback
        self.audio_buffer = []
        
        try:
            import sounddevice as sd
            
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"Audio status: {status}")
                if self.is_recording:
                    self.audio_buffer.append(indata.copy())
            
            # Start recording stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=self.chunk_size
            )
            self.stream.start()
            
            print("✓ Recording started")
            return True
            
        except Exception as e:
            print(f"Recording start error: {e}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and return transcription"""
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        # Stop stream
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        # Process recorded audio
        if self.audio_buffer:
            audio_data = np.concatenate(self.audio_buffer, axis=0)
            transcription = self._transcribe_audio(audio_data)
            
            if self.callback and transcription:
                self.callback(transcription)
            
            return transcription
        
        return None
    
    def _transcribe_audio(self, audio_data: np.ndarray) -> Optional[str]:
        """Transcribe audio data"""
        if not self.transcriber or len(audio_data) == 0:
            return None
        
        try:
            # Normalize audio
            audio_data = audio_data.flatten().astype(np.float32)
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Transcribe
            segments, info = self.transcriber.transcribe(
                audio_data,
                language=self.transcription_language,
                beam_size=5
            )
            
            # Combine segments
            transcription = " ".join([segment.text for segment in segments])
            
            return transcription.strip() if transcription else None
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def record_and_transcribe(self, duration: float = 5.0) -> Optional[str]:
        """Record for specified duration and transcribe"""
        print(f"Recording for {duration} seconds...")
        
        if not self.start_recording():
            return None
        
        # Record for specified duration
        time.sleep(duration)
        
        return self.stop_recording()
    
    def save_audio_to_file(self, filename: Optional[str] = None) -> Optional[str]:
        """Save current recording to file"""
        if not self.audio_buffer:
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audio_{timestamp}.wav"
        
        try:
            audio_data = np.concatenate(self.audio_buffer, axis=0)
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                
                # Convert to 16-bit PCM
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())
            
            self.audio_files.append(filename)
            print(f"✓ Audio saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"Save audio error: {e}")
            return None
    
    def transcribe_file(self, filepath: str) -> Optional[str]:
        """Transcribe an existing audio file"""
        if not self.transcriber:
            if not self.initialize():
                return None
        
        try:
            segments, info = self.transcriber.transcribe(
                filepath,
                language=self.transcription_language
            )
            
            transcription = " ".join([segment.text for segment in segments])
            return transcription.strip()
            
        except Exception as e:
            print(f"File transcription error: {e}")
            return None
    
    def list_audio_files(self) -> List[str]:
        """List all recorded audio files"""
        return self.audio_files.copy()
    
    def get_stats(self) -> Dict:
        """Get recording statistics"""
        total_duration = sum(len(buf) for buf in self.audio_buffer) / self.sample_rate
        
        return {
            'initialized': self.initialized,
            'is_recording': self.is_recording,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'buffer_duration_sec': total_duration,
            'audio_files_count': len(self.audio_files),
            'model_loaded': self.transcriber is not None
        }
    
    def set_language(self, language: str):
        """Set transcription language"""
        self.transcription_language = language
        print(f"Transcription language set to: {language}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_recording()
        self.audio_buffer = []
