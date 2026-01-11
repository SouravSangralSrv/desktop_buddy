"""
Text-to-Speech Handler with Multiple Engine Support
Supports Piper TTS (anime-style voice) and Edge-TTS (fallback)
"""

import asyncio
import edge_tts
import pygame
import os
import tempfile
import subprocess
from pathlib import Path


class PiperTTSEngine:
    """Piper TTS engine for anime-style female voice"""
    
    def __init__(self, model="en_US-lessac-medium", speed=1.2):
        self.model = model
        self.speed = speed
        self.piper_available = self._check_piper()
        
    def _check_piper(self):
        """Check if Piper TTS is available"""
        try:
            result = subprocess.run(
                ["piper", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("⚠️ Piper TTS command not found, will use fallback")
            return False
    
    def generate_audio(self, text, output_file):
        """Generate audio using Piper TTS"""
        if not self.piper_available:
            return False
        
        try:
            # Piper command: echo text | piper --model model --output_file output.wav
            cmd = [
                "piper",
                "--model", self.model,
                "--output_file", output_file,
                "--length_scale", str(1.0 / self.speed)  # Speed control
            ]
            
            # Run Piper with text as input
            process = subprocess.run(
                cmd,
                input=text,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if process.returncode == 0 and os.path.exists(output_file):
                return True
            else:
                print(f"Piper TTS error: {process.stderr}")
                return False
                
        except Exception as e:
            print(f"Error generating Piper audio: {e}")
            return False


class EdgeTTSEngine:
    """Edge TTS engine as fallback"""
    
    def __init__(self, voice="en-US-AnaNeural", rate="+20%"):
        self.voice = voice
        self.rate = rate
    
    async def _generate_audio_async(self, text, output_file):
        """Generate audio using Edge TTS"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(output_file)
    
    def generate_audio(self, text, output_file):
        """Generate audio synchronously"""
        try:
            asyncio.run(self._generate_audio_async(text, output_file))
            return os.path.exists(output_file)
        except Exception as e:
            print(f"Error generating Edge TTS audio: {e}")
            return False


class TTSHandler:
    """
    Multi-engine TTS Handler
    Tries Piper TTS first (anime voice), falls back to Edge TTS
    """
    
    def __init__(self, engine="piper", config=None):
        pygame.mixer.init(frequency=22050)  # Match Piper's sample rate
        self.is_speaking = False
        self.should_stop = False
        
        # Load config or use defaults
        if config:
            # Check for voice preset
            preset_name = config.get("voice_preset", None)
            presets = config.get("voice_presets", {})
            
            if preset_name and preset_name in presets:
                # Load from preset
                preset = presets[preset_name]
                edge_voice = preset.get("edge_voice", "en-US-AnaNeural")
                speed = preset.get("speed", 1.2)
                print(f"🎤 Using voice preset: {preset_name} - {preset.get('description', '')}")
            else:
                # Load from voice config
                edge_voice = config.get("voice", {}).get("edge_voice", "en-US-AnaNeural")
                speed = config.get("voice", {}).get("speed", 1.2)
            
            piper_model = config.get("voice", {}).get("piper_model", "en_US-lessac-medium")
            edge_rate = f"+{int((speed - 1) * 100)}%"
        else:
            piper_model = "en_US-lessac-medium"
            edge_voice = "en-US-AnaNeural"
            speed = 1.2
            edge_rate = "+20%"
        
        # Initialize engines
        self.piper_engine = PiperTTSEngine(model=piper_model, speed=speed)
        self.edge_engine = EdgeTTSEngine(voice=edge_voice, rate=edge_rate)
        
        # Set primary engine
        self.use_piper = (engine == "piper" and self.piper_engine.piper_available)
        
        if self.use_piper:
            print("🎤 Using Piper TTS (anime voice)")
        else:
            print(f"🎤 Using Edge TTS: {edge_voice}")
    
    def stop(self):
        """Stop TTS playback immediately"""
        self.should_stop = True
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.is_speaking = False
    
    def speak(self, text, interrupt_callback=None):
        """Speak the given text using available TTS engine
        
        Args:
            text: Text to speak
            interrupt_callback: Optional function that returns True if should interrupt
        """
        if not text:
            return
        
        self.is_speaking = True
        self.should_stop = False
        
        try:
            # Create temporary file
            suffix = ".wav" if self.use_piper else ".mp3"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fp:
                temp_filename = fp.name
            
            # Try Piper first, fallback to Edge if it fails
            success = False
            if self.use_piper:
                success = self.piper_engine.generate_audio(text, temp_filename)
                if not success:
                    print("Piper failed, falling back to Edge TTS")
                    # Try Edge TTS fallback
                    os.remove(temp_filename)
                    temp_filename = temp_filename.replace(".wav", ".mp3")
                    success = self.edge_engine.generate_audio(text, temp_filename)
            else:
                success = self.edge_engine.generate_audio(text, temp_filename)
            
            if not success:
                print("❌ TTS generation failed")
                return
            
            # Play audio
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish or stop signal, checking for interrupts
            while pygame.mixer.music.get_busy() and not self.should_stop:
                # Check for voice interrupt if callback provided
                if interrupt_callback and interrupt_callback():
                    print("\n🔇 Interrupted by voice!")
                    self.should_stop = True
                    break
                pygame.time.Clock().tick(10)
            
            # Stop if interrupted
            if self.should_stop:
                pygame.mixer.music.stop()
            
            # Cleanup
            pygame.mixer.music.unload()
            
            # Small delay before removing file (Windows can be finicky)
            pygame.time.wait(100)
            
            try:
                os.remove(temp_filename)
            except Exception as e:
                print(f"Warning: Could not remove temp file: {e}")
            
        except Exception as e:
            print(f"Error in TTS: {e}")
        finally:
            self.is_speaking = False
            self.should_stop = False
