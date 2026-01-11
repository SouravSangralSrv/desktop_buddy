import sys
import os
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject

# Check for first run and launch setup wizard if needed
if not os.path.exists('config.json'):
    from setup_wizard import run_setup_wizard
    print("🎉 Welcome to Desktop Buddy! Running first-time setup...")
    # Note: Setup wizard will create its own QApplication
    if not run_setup_wizard():
        print("Setup cancelled. Exiting.")
        sys.exit(0)

from ui.window import DesktopWindow
from core.llm import LLMHandler
from core.stt import STTHandler
from core.tts import TTSHandler
from core.actions import SystemActions
from core.sentiment import SentimentAnalyzer, Mood

class WorkerSignals(QObject):
    speaking_state = pyqtSignal(bool)
    listening_state = pyqtSignal(bool)
    thinking_state = pyqtSignal(bool)
    assistant_response = pyqtSignal(str)
    user_voice_input = pyqtSignal(str)
    action_feedback = pyqtSignal(str)
    llm_backend_changed = pyqtSignal(str)  # Signal for backend changes
    mood_detected = pyqtSignal(str, str)  # Signal for mood detection (mood_name, description)

class AssistantThread(QThread):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.running = True
        
        # Load config
        self.config = self.load_config()
        
        # Initialize components
        self.llm = LLMHandler()
        self.stt = STTHandler()
        self.tts = TTSHandler(
            engine=self.config.get('tts', {}).get('engine', 'piper'),
            config=self.config.get('tts', {})
        )
        self.actions = SystemActions()
        self.sentiment = SentimentAnalyzer(sensitivity=0.5)
        self.voice_enabled = True
    
    def load_config(self):
        """Load configuration from config.json"""
        import json
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def run(self):
        while self.running:
            if self.voice_enabled:
                # Stop any ongoing TTS before listening
                if self.tts.is_speaking:
                    self.tts.stop()
                
                print("Assistant: Listening...")
                self.signals.listening_state.emit(True)
                user_input = self.stt.listen()
                self.signals.listening_state.emit(False)
                
                if user_input:
                    print(f"User said: {user_input}")
                    self.signals.user_voice_input.emit(user_input)
                    
                    # Simple exit command
                    if "goodbye" in user_input.lower() or "exit" in user_input.lower():
                        response = "Goodbye!"
                        self.signals.assistant_response.emit(response)
                        self.signals.speaking_state.emit(True)
                        self.tts.speak(response)
                        self.signals.speaking_state.emit(False)
                        self.running = False
                        QApplication.quit()
                        break

                    self.process_input(user_input, use_tts=True)
    
    
    def analyze_and_process_mood(self, user_input):
        """Analyze user mood and set LLM context accordingly"""
        analysis = self.sentiment.analyze(user_input)
        mood = analysis['mood']
        confidence = analysis['confidence']
        
        print(f"Mood detected: {mood.value} (confidence: {confidence:.2f})")
        
        # Emit mood signal to UI
        mood_description = self.sentiment.get_mood_description(mood)
        self.signals.mood_detected.emit(mood.value, mood_description)
        
        # Set empathetic context for LLM
        if confidence > 0.4:  # Only set context if reasonably confident
            empathy_context = self.sentiment.get_empathetic_context(analysis)
            self.llm.set_mood_context(empathy_context)
        else:
            self.llm.set_mood_context("")  # Clear context for neutral
    
    def process_input(self, user_input, use_tts=False):
        """Process user input through LLM and execute any actions"""
        
        # Analyze mood first
        self.analyze_and_process_mood(user_input)
        
        # Log user message
        self.actions.save_chat_message("User", user_input)
        
        self.signals.thinking_state.emit(True)
        result = self.llm.chat(user_input)
        self.signals.thinking_state.emit(False)
        response_text = result['text']
        actions = result['actions']
        backend = result.get('backend', '💻 Ollama')
        
        # Log assistant response
        self.actions.save_chat_message("Assistant", response_text)
        
        # Emit backend info
        self.signals.llm_backend_changed.emit(backend)
        
        print(f"Assistant ({backend}): {response_text}")
        
        # Send text response to UI
        if response_text:
            self.signals.assistant_response.emit(response_text)
            
            # Speak if voice mode - with interrupt detection
            if use_tts:
                self.signals.speaking_state.emit(True)
                
                # Create interrupt callback that checks if user is speaking
                def check_interrupt():
                    return self.stt.is_speaking(duration=0.2)
                
                # Speak with interrupt detection
                self.tts.speak(response_text, interrupt_callback=check_interrupt)
                
                self.signals.speaking_state.emit(False)
                
                # If interrupted, immediately start listening again
                if self.tts.should_stop:
                    print("🎤 Listening after interrupt...")
                    self.signals.listening_state.emit(True)
                    user_input = self.stt.listen()
                    self.signals.listening_state.emit(False)
                    
                    if user_input:
                        print(f"User said (after interrupt): {user_input}")
                        self.signals.user_voice_input.emit(user_input)
                        # Process the new input
                        self.process_input(user_input, use_tts=True)
        
        # Execute actions
        if actions:
            for action in actions:
                print(f"Executing action: {action}")
                feedback = self.actions.execute_action(action['type'], action['params'])
                print(f"Action result: {feedback}")
                
                # Send action feedback to UI
                self.signals.action_feedback.emit(feedback)
    
    @pyqtSlot(str)
    def handle_text_message(self, message):
        """Handle text messages from the chat UI"""
        print(f"User typed: {message}")
        
        # Check for exit command
        if "goodbye" in message.lower() or "exit" in message.lower():
            response = "Goodbye!"
            self.signals.assistant_response.emit(response)
            self.running = False
            QApplication.quit()
            return
        
        # Process through LLM with action detection
        self.process_input(message, use_tts=False)
    
    @pyqtSlot(str)
    def switch_backend(self, mode):
        """Switch LLM backend mode"""
        print(f"🔄 Switching LLM backend to: {mode}")
        self.config['llm']['mode'] = mode
        # Update config file
        import json
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Backend mode updated to: {mode}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = DesktopWindow()
    
    signals = WorkerSignals()
    signals.speaking_state.connect(window.set_speaking)
    signals.listening_state.connect(window.set_listening)
    signals.thinking_state.connect(lambda thinking: window.set_thinking() if thinking else None)
    signals.assistant_response.connect(window.add_assistant_message)
    signals.user_voice_input.connect(lambda msg: window.add_message("You (voice)", msg, is_user=True))
    signals.action_feedback.connect(lambda msg: window.add_message("System", msg, is_user=False))
    signals.llm_backend_changed.connect(window.update_llm_status)
    signals.mood_detected.connect(window.on_mood_detected)
    
    # Set base_y for character animations after window is positioned
    window.character.base_y = window.character.y()
    
    assistant = AssistantThread(signals)
    
    # Connect text chat to assistant
    window.text_message_sent.connect(assistant.handle_text_message)
    
    # Connect backend switcher
    window.backend_switch_requested.connect(assistant.switch_backend)
    
    assistant.start()
    
    sys.exit(app.exec_())
