import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                              QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
import os
from ui.character import AnimatedCharacter, Expression, ExpressionManager

class DesktopWindow(QWidget):
    # Signal to send text messages to the assistant
    text_message_sent = pyqtSignal(str)
    # Signal to change LLM backend
    backend_switch_requested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.oldPos = self.pos()
        self.chat_visible = True

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Avatar section
        avatar_widget = QWidget()
        avatar_widget.setStyleSheet("background: transparent;")
        avatar_layout = QVBoxLayout()
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use animated character instead of static image
        self.character = AnimatedCharacter(self, size=300)
        avatar_layout.addWidget(self.character)
        avatar_widget.setLayout(avatar_layout)
        
        # Expression manager for context-aware expressions
        self.expression_manager = ExpressionManager()
        self.expression_manager.expression_request.connect(
            lambda expr: self.character.set_expression(expr)
        )
        
        # Chat section
        chat_widget = QWidget()
        chat_widget.setFixedWidth(400)
        chat_widget.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                border-radius: 10px;
            }
        """)
        
        chat_layout = QVBoxLayout()
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(10)
        
        # Title bar with close button
        title_bar = QHBoxLayout()
        title_bar.setSpacing(10)
        
        title_label = QLabel("💬 Chat with Desktop Buddy")
        title_label.setStyleSheet("""
            QLabel {
                color: #cdd6f4;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                padding: 5px;
            }
        """)
        
        # LLM status indicator (clickable to switch)
        self.llm_status_label = QPushButton("💻 Ollama")
        self.llm_status_label.setFixedHeight(25)
        self.llm_status_label.setCursor(Qt.PointingHandCursor)
        self.llm_status_label.setStyleSheet("""
            QPushButton {
                color: #89b4fa;
                font-size: 11px;
                background: rgba(137, 180, 250, 0.1);
                border: 1px solid #89b4fa;
                border-radius: 8px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background: rgba(137, 180, 250, 0.2);
            }
        """)
        self.llm_status_label.clicked.connect(self.toggle_llm_backend)
        self.current_backend = "auto"  # Track current mode
        
        # Mood status indicator
        self.mood_status_label = QLabel("😐 Neutral")
        self.mood_status_label.setStyleSheet("""
            QLabel {
                color: #cba6f7;
                font-size: 11px;
                background: rgba(203, 166, 247, 0.1);
                border: 1px solid #cba6f7;
                border-radius: 8px;
                padding: 3px 8px;
            }
        """)
        
        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #eba0ac;
            }
            QPushButton:pressed {
                background-color: #f2cdcd;
            }
        """)
        close_button.clicked.connect(self.close_application)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.mood_status_label)
        title_bar.addWidget(self.llm_status_label)
        title_bar.addWidget(close_button)
        
        chat_layout.addLayout(title_bar)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial;
            }
        """)
        chat_layout.addWidget(self.chat_history)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type a message...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 2px solid #313244;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #89b4fa;
            }
        """)
        self.text_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #89dceb;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(input_layout)
        chat_widget.setLayout(chat_layout)
        
        # Add sections to main layout
        main_layout.addWidget(avatar_widget)
        main_layout.addWidget(chat_widget)
        
        self.setLayout(main_layout)
        
        # Set window properties
        self.setStyleSheet("background-color: rgba(30, 30, 46, 200);")
        
        # Position bottom right
        screen_geometry = QApplication.desktop().availableGeometry()
        window_width = 750
        window_height = 500
        self.resize(window_width, window_height)
        self.move(screen_geometry.width() - window_width - 20, 
                  screen_geometry.height() - window_height - 50)
        self.show()

    def load_avatar(self, path):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.avatar_label.setPixmap(scaled_pixmap)
            self.avatar_label.setFixedSize(300, 300)
        else:
            self.avatar_label.setText("Avatar\nnot found")
            self.avatar_label.setStyleSheet("color: white; font-size: 14px;")
            self.avatar_label.setAlignment(Qt.AlignCenter)

    def close_application(self):
        """Close the desktop buddy application"""
        QApplication.quit()
    @pyqtSlot()
    def send_message(self):
        """Handle sending a text message"""
        message = self.text_input.text().strip()
        if message:
            # Add user message to chat
            self.add_message("You", message, is_user=True)
            
            # Make character react to the message
            self.character.react_to_message(message)
            
            # Clear input field
            self.text_input.clear()
            
            # Send message to assistant
            self.text_message_sent.emit(message)
    
    def add_message(self, sender, message, is_user=False):
        color = "#89b4fa" if is_user else "#a6e3a1"
        formatted_message = f'<p style="margin: 5px 0;"><span style="color: {color}; font-weight: bold;">{sender}:</span> <span style="color: #cdd6f4;">{message}</span></p>'
        self.chat_history.append(formatted_message)
        # Auto-scroll to bottom
        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    @pyqtSlot(bool)
    def set_speaking(self, is_speaking):
        """Update character to show speaking/talking animation"""
        if is_speaking:
            self.character.start_talking()
        else:
            self.character.stop_talking()
    
    @pyqtSlot(bool)
    def set_listening(self, is_listening):
        """Update character to show listening expression"""
        if is_listening:
            self.character.set_listening()
        else:
            self.character.set_neutral()
    
    def set_thinking(self):
        """Update character to show thinking expression"""
        self.character.set_thinking()
    
    @pyqtSlot(str)
    def update_llm_status(self, backend_name):
        """Update the LLM status indicator"""
        self.llm_status_label.setText(backend_name)
        
        # Change color based on backend
        if "Gemini" in backend_name:
            color = "#a6e3a1"  # Green for online
        elif "Ollama" in backend_name:
            color = "#89b4fa"  # Blue for offline
        else:
            color = "#f38ba8"  # Red for error
        
        self.llm_status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                background: rgba(137, 180, 250, 0.1);
                border: 1px solid {color};
                border-radius: 8px;
                padding: 3px 8px;
            }}
        """)
    
    @pyqtSlot(str)
    def add_assistant_message(self, message):
        """Add assistant message and update expression based on sentiment"""
        self.add_message("Assistant", message, is_user=False)
        
        # Analyze sentiment and set appropriate expression after speaking
        expression = self.expression_manager.analyze_sentiment(message)
        # Slight delay to let talking animation finish
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, lambda: self.character.set_expression(expression))
    
    @pyqtSlot(str, str)
    def on_mood_detected(self, mood_name, mood_description):
        """Handle mood detection and update UI"""
        # Update mood indicator
        self.mood_status_label.setText(mood_description)
        
        # Change color based on mood
        mood_colors = {
            "happy": "#a6e3a1",  # Green
            "excited": "#f9e2af",  # Yellow
            "sad": "#89b4fa",  # Blue
            "anxious": "#f38ba8",  # Red/Pink
            "angry": "#f38ba8",  # Red
            "worried": "#fab387",  # Orange
            "neutral": "#cba6f7"  # Purple
        }
        
        color = mood_colors.get(mood_name, "#cba6f7")
        
        self.mood_status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11px;
                background: rgba(203, 166, 247, 0.1);
                border: 1px solid {color};
                border-radius: 8px;
                padding: 3px 8px;
            }}
        """)
        
        # Update character animation based on mood
        self.character.set_mood_animation(mood_name)
        
        print(f"UI updated with mood: {mood_name} - {mood_description}")
    
    def toggle_llm_backend(self):
        """Toggle between Ollama, Gemini, Groq, and Auto modes"""
        # Cycle through: auto -> ollama -> gemini -> groq -> auto
        if self.current_backend == "auto":
            self.current_backend = "ollama"
            self.llm_status_label.setText("💻 Ollama (Forced)")
            self.backend_switch_requested.emit("ollama")
            self.add_message("System", "Switched to Ollama (offline)", is_user=False)
        elif self.current_backend == "ollama":
            self.current_backend = "gemini"
            self.llm_status_label.setText("🌐 Gemini (Forced)")
            self.backend_switch_requested.emit("gemini")
            self.add_message("System", "Switched to Gemini (Google AI)", is_user=False)
        elif self.current_backend == "gemini":
            self.current_backend = "groq"
            self.llm_status_label.setText("⚡ Groq (Forced)")
            self.backend_switch_requested.emit("groq")
            self.add_message("System", "Switched to Groq (FREE & FAST!)", is_user=False)
        else:  # groq
            self.current_backend = "auto"
            self.llm_status_label.setText("🔄 Auto")
            self.backend_switch_requested.emit("auto")
            self.add_message("System", "Switched to Auto mode (smart selection)", is_user=False)
        
        print(f"🔄 Backend switched to: {self.current_backend}")
