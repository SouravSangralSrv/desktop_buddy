"""
Speech Recognition Handler with Voice Activity Detection
Supports background listening and interrupt detection
"""

import speech_recognition as sr
import threading
import time


class STTHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Voice activity detection settings
        self.energy_threshold = 300  # Adjust based on your environment
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        
        # Adjust for ambient noise
        with self.microphone as source:
            print("⚙️ Calibrating microphone for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"✅ Energy threshold set to {self.recognizer.energy_threshold}")
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """Listen for voice input with timeout"""
        with self.microphone as source:
            print("🎤 Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Heard: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                return None
    
    def is_speaking(self, duration=0.5):
        """
        Detect if user is currently speaking
        Used for interrupt detection during TTS playback
        
        Args:
            duration: How long to listen for voice activity (seconds)
        
        Returns:
            bool: True if voice detected, False otherwise
        """
        try:
            with self.microphone as source:
                # Quick check for audio above threshold
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                # If we got audio, someone is speaking
                return True
        except sr.WaitTimeoutError:
            # No voice detected in time window
            return False
        except Exception as e:
            # Error in detection, assume not speaking
            return False
    
    def listen_for_interrupt(self, callback, stop_event):
        """
        Background thread to monitor for voice interrupts
        
        Args:
            callback: Function to call when interrupt detected
            stop_event: Threading event to signal when to stop monitoring
        """
        while not stop_event.is_set():
            if self.is_speaking(duration=0.3):
                # User started speaking!
                callback()
                break
            time.sleep(0.1)  # Check every 100ms
