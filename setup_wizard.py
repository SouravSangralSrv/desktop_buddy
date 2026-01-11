"""
First-Run Setup Wizard for Desktop Buddy
Helps users configure API keys and settings on first launch
"""
import sys
import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QTextEdit,
                             QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.ollama_utils import get_installed_ollama_models, is_ollama_running, suggest_model_to_pull


class SetupWizard(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Buddy - First Time Setup")
        self.setModal(True)
        self.resize(600, 500)
        
        self.config = self.load_default_config()
        self.ollama_models = []  # Will store detected Ollama models
        self.init_ui()
    
    def load_default_config(self):
        """Load default configuration"""
        return {
            "llm": {
                "mode": "groq",
                "ollama_model": "llama3.2:latest",
                "gemini_model": "gemini-pro",
                "gemini_api_key": "",
                "groq_api_key": "",
                "groq_model": "llama-3.3-70b-versatile"
            },
            "preferences": {
                "prefer_online": True,
                "auto_fallback": True
            },
            "sentiment": {
                "enabled": True,
                "sensitivity": 0.5,
                "empathy_mode": True
            },
            "tts": {
                "engine": "edge",
                "fallback_engine": "edge",
                "voice_preset": "indian_english",
                "voice": {
                    "edge_voice": "en-IN-NeerjaNeural",
                    "speed": 1.15,
                    "pitch_shift": 1.15
                }
            }
        }
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Welcome to Desktop Buddy! 🎉")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Let's set up your AI companion")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # LLM Backend Selection
        layout.addWidget(QLabel("<b>1. Choose Your AI Backend:</b>"))
        
        self.backend_group = QButtonGroup()
        
        # Groq option (recommended)
        groq_radio = QRadioButton("⚡ Groq (Recommended - Fast & Free!)")
        groq_radio.setChecked(True)
        self.backend_group.addButton(groq_radio, 1)
        layout.addWidget(groq_radio)
        
        groq_info = QLabel("   Free API, fastest responses, great quality")
        groq_info.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(groq_info)
        
        # Gemini option
        gemini_radio = QRadioButton("🌐 Google Gemini")
        self.backend_group.addButton(gemini_radio, 2)
        layout.addWidget(gemini_radio)
        
        gemini_info = QLabel("   Google's AI, high quality responses")
        gemini_info.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(gemini_info)
        
        # Ollama option
        ollama_radio = QRadioButton("💻 Ollama (Local/Offline)")
        self.backend_group.addButton(ollama_radio, 3)
        layout.addWidget(ollama_radio)
        
        ollama_info = QLabel("   Runs locally, no internet needed (requires Ollama installed)")
        ollama_info.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(ollama_info)
        
        # Ollama model selection (shown when Ollama is selected)
        ollama_model_layout = QHBoxLayout()
        ollama_model_layout.addSpacing(30)  # Indent
        ollama_model_layout.addWidget(QLabel("Ollama Model:"))
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEnabled(False)  # Disabled until Ollama selected
        ollama_model_layout.addWidget(self.ollama_model_combo)
        
        # Refresh button to detect models
        refresh_btn = QPushButton("🔄 Detect Models")
        refresh_btn.clicked.connect(self.detect_ollama_models)
        ollama_model_layout.addWidget(refresh_btn)
        layout.addLayout(ollama_model_layout)
        
        # Ollama status label
        self.ollama_status_label = QLabel("")
        self.ollama_status_label.setStyleSheet("color: #888; font-size: 9pt; margin-left: 30px;")
        layout.addWidget(self.ollama_status_label)
        
        # Connect radio button to enable/disable Ollama model selection
        ollama_radio.toggled.connect(lambda checked: self.on_ollama_selected(checked))
        
        layout.addSpacing(15)
        
        # API Key inputs
        layout.addWidget(QLabel("<b>2. Enter API Key (if using Groq or Gemini):</b>"))
        
        # Groq API Key
        groq_layout = QHBoxLayout()
        groq_layout.addWidget(QLabel("Groq API Key:"))
        self.groq_key_input = QLineEdit()
        self.groq_key_input.setPlaceholderText("Get free key from console.groq.com")
        groq_layout.addWidget(self.groq_key_input)
        layout.addLayout(groq_layout)
        
        # Gemini API Key
        gemini_layout = QHBoxLayout()
        gemini_layout.addWidget(QLabel("Gemini API Key:"))
        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setPlaceholderText("Optional - from makersuite.google.com")
        gemini_layout.addWidget(self.gemini_key_input)
        layout.addLayout(gemini_layout)
        
        # Help link
        help_label = QLabel('<a href="https://console.groq.com">Get Free Groq API Key →</a>')
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #4A90E2;")
        layout.addWidget(help_label)
        
        layout.addSpacing(15)
        
        # Voice preset
        layout.addWidget(QLabel("<b>3. Choose Voice Style:</b>"))
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "Indian English (Friendly)",
            "American English (Anime)",
            "Hinglish"
        ])
        voice_layout.addWidget(self.voice_combo)
        layout.addLayout(voice_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        skip_btn = QPushButton("Skip Setup (Use Defaults)")
        skip_btn.clicked.connect(self.skip_setup)
        button_layout.addWidget(skip_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save & Start Desktop Buddy")
        save_btn.clicked.connect(self.save_config)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Auto-detect Ollama models on startup
        self.detect_ollama_models()
    
    def detect_ollama_models(self):
        """Detect installed Ollama models"""
        if not is_ollama_running():
            self.ollama_status_label.setText("⚠️ Ollama not running. Install from ollama.ai")
            self.ollama_model_combo.clear()
            self.ollama_model_combo.addItem("(Ollama not detected)")
            return
        
        models = get_installed_ollama_models()
        self.ollama_models = models
        
        self.ollama_model_combo.clear()
        
        if not models:
            self.ollama_status_label.setText(f"⚠️ No models found. Suggested: ollama pull {suggest_model_to_pull()}")
            self.ollama_model_combo.addItem(suggest_model_to_pull())
        else:
            self.ollama_status_label.setText(f"✅ Found {len(models)} model(s)")
            for model in models:
                self.ollama_model_combo.addItem(model['display_name'])
    
    def on_ollama_selected(self, checked):
        """Called when Ollama radio button is toggled"""
        self.ollama_model_combo.setEnabled(checked)
        if checked:
            self.detect_ollama_models()
    
    def save_config(self):
        """Save configuration and close wizard"""
        # Get selected backend
        backend_id = self.backend_group.checkedId()
        if backend_id == 1:
            self.config['llm']['mode'] = 'groq'
        elif backend_id == 2:
            self.config['llm']['mode'] = 'gemini'
        else:
            self.config['llm']['mode'] = 'ollama'
        
        # Get API keys
        groq_key = self.groq_key_input.text().strip()
        gemini_key = self.gemini_key_input.text().strip()
        
        # Validate: if Groq selected, need Groq key
        if backend_id == 1 and not groq_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Groq API key is required for Groq mode.\n\n"
                "Get a free key from: https://console.groq.com\n\n"
                "Or choose 'Ollama (Local)' to run offline."
            )
            return
        
        if backend_id == 2 and not gemini_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Gemini API key is required for Gemini mode.\n\n"
                "Or choose 'Groq (Free)' or 'Ollama (Local)' instead."
            )
            return
        
        # Save keys
        if groq_key:
            self.config['llm']['groq_api_key'] = groq_key
        if gemini_key:
            self.config['llm']['gemini_api_key'] = gemini_key
        
        # Save Ollama model if Ollama mode selected
        if backend_id == 3:  # Ollama
            selected_model = self.ollama_model_combo.currentText()
            if selected_model and selected_model != "(Ollama not detected)":
                self.config['llm']['ollama_model'] = selected_model
            else:
                # Use default if none selected
                self.config['llm']['ollama_model'] = suggest_model_to_pull()
        
        # Voice preset
        voice_index = self.voice_combo.currentIndex()
        presets = ["indian_english", "anime_english", "hinglish"]
        self.config['tts']['voice_preset'] = presets[voice_index]
        
        # Save to config.json
        try:
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            
            QMessageBox.information(
                self,
                "Setup Complete!",
                "Configuration saved successfully!\n\n"
                "Desktop Buddy will now start."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save configuration:\n{e}"
            )
    
    def skip_setup(self):
        """Skip setup and use defaults"""
        reply = QMessageBox.question(
            self,
            "Skip Setup?",
            "This will use default settings (Ollama local mode).\n\n"
            "You can configure it later by editing config.json.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config['llm']['mode'] = 'ollama'
            try:
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save config:\n{e}")


def run_setup_wizard():
    """Run the setup wizard"""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    result = wizard.exec_()
    return result == QDialog.Accepted


if __name__ == '__main__':
    run_setup_wizard()
