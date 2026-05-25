"""
Voice Recording Service
Real-time microphone recording with Faster-Whisper transcription
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
import threading
import io
import wave


class VoiceRecordingService:
    """
    Voice recording service with:
    - Real-time microphone capture
    - Local transcription via Faster-Whisper
    - Contextual speech memory
    """
    
    def __init__(self, context_engine=None, model_size: str = "base"):
        self.context_engine = context_engine
        self.model_size = model_size  # tiny, base, small, medium, large
        self.is_running = False
        self.is_recording = False
        self._record_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._whisper_model = None
        self._audio_buffer = []
        self._sample_rate = 16000
        self._chunk_duration = 5.0  # Transcribe every 5 seconds
        
        # Voice activity detection
        self._vad_active = False
        self._silence_threshold = 0.01
        self._silence_duration = 1.0
    
    async def start(self):
        """Initialize Whisper model and start recording"""
        try:
            # Load Whisper model
            from faster_whisper import WhisperModel
            
            print(f"🎤 Loading Whisper model ({self.model_size})...")
            self._whisper_model = WhisperModel(
                self.model_size,
                device="cpu",  # Can be changed to "cuda" for GPU
                compute_type="int8"
            )
            print("✅ Whisper model loaded")
            
            # Start recording thread
            self.is_running = True
            self._stop_event.clear()
            self._record_thread = threading.Thread(target=self._recording_loop)
            self._record_thread.daemon = True
            self._record_thread.start()
            
            print("🎤 Voice recording started")
            
        except ImportError:
            print("Warning: faster-whisper not installed, voice recording disabled")
            self.is_running = False
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop voice recording"""
        self._stop_event.set()
        self.is_running = False
        self.is_recording = False
        
        if self._record_thread:
            self._record_thread.join(timeout=2.0)
        
        print("🎤 Voice recording stopped")
    
    def _recording_loop(self):
        """Main recording loop running in separate thread"""
        try:
            import sounddevice as sd
            import numpy as np
            
            # Audio queue for buffering
            audio_chunks = []
            chunk_samples = int(self._sample_rate * self._chunk_duration)
            
            # Callback for audio stream
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"Audio stream status: {status}")
                
                if self._stop_event.is_set():
                    return
                
                # Store audio chunk
                audio_data = indata.copy().flatten()
                audio_chunks.append(audio_data)
                
                # Check if we have enough data for transcription
                total_samples = sum(len(chunk) for chunk in audio_chunks)
                
                if total_samples >= chunk_samples:
                    # Combine chunks
                    combined_audio = np.concatenate(audio_chunks)
                    audio_chunks.clear()
                    
                    # Transcribe in background
                    if self.is_recording:
                        self._transcribe_audio(combined_audio)
            
            # Start audio stream
            with sd.InputStream(
                samplerate=self._sample_rate,
                channels=1,
                dtype='float32',
                callback=audio_callback,
                blocksize=1024
            ) as stream:
                self.is_recording = True
                
                while not self._stop_event.is_set():
                    self._stop_event.wait(0.1)
                
                self.is_recording = False
                
        except ImportError:
            print("Warning: sounddevice or numpy not installed, voice recording disabled")
            self._stop_event.wait()
        except Exception as e:
            print(f"Voice recording error: {e}")
            self._stop_event.wait(1.0)
    
    def _transcribe_audio(self, audio_data):
        """Transcribe audio chunk using Whisper"""
        try:
            if not self._whisper_model or not self.is_recording:
                return
            
            # Check if audio has significant content (simple VAD)
            audio_level = abs(audio_data).mean()
            if audio_level < self._silence_threshold:
                return  # Skip silent chunks
            
            # Transcribe
            segments, info = self._whisper_model.transcribe(
                audio_data,
                language="en",  # Can be auto-detected
                beam_size=5,
                vad_filter=True
            )
            
            # Collect transcription
            transcription_parts = []
            for segment in segments:
                transcription_parts.append(segment.text.strip())
            
            full_transcription = " ".join(transcription_parts)
            
            if full_transcription:
                timestamp = datetime.now().isoformat()
                
                # Send to context engine
                if self.context_engine:
                    import asyncio
                    asyncio.run_coroutine_threadsafe(
                        self.context_engine.process_data({
                            "type": "voice",
                            "timestamp": timestamp,
                            "data": {
                                "transcription": full_transcription,
                                "language": info.language,
                                "duration": len(audio_data) / self._sample_rate,
                                "audio_level": float(audio_level)
                            }
                        }),
                        asyncio.get_event_loop()
                    )
                
                print(f"🗣️  Transcribed: {full_transcription[:100]}...")
                
        except Exception as e:
            print(f"Transcription error: {e}")
    
    def save_audio(self, audio_data: bytes, filename: str = None) -> str:
        """Save audio to WAV file"""
        import uuid
        from pathlib import Path
        
        if filename is None:
            filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.wav"
        
        # Save to sessions directory
        sessions_path = Path("./sessions/audio")
        sessions_path.mkdir(parents=True, exist_ok=True)
        filepath = sessions_path / filename
        
        # Write WAV file
        with wave.open(str(filepath), 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self._sample_rate)
            wav_file.writeframes(audio_data)
        
        return str(filepath)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current recording status"""
        return {
            "is_running": self.is_running,
            "is_recording": self.is_recording,
            "model_loaded": self._whisper_model is not None,
            "model_size": self.model_size,
            "sample_rate": self._sample_rate,
            "vad_active": self._vad_active
        }
