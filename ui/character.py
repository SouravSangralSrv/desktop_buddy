import os
from enum import Enum
from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject, QRect, pyqtProperty
from PyQt5.QtGui import QPixmap, QTransform
import random
import math


class Expression(Enum):
    """Available character expressions"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    TALKING = "talking"
    LISTENING = "listening"
    THINKING = "thinking"
    EXCITED = "excited"
    SAD = "sad"
    COMFORTING = "comforting"
    ENCOURAGING = "encouraging"
    WORRIED = "worried"


class AnimatedCharacter(QLabel):
    """Animated character widget with expression changes and transitions"""
    
    expression_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, size=300):
        super().__init__(parent)
        self.size = size
        self.current_expression = Expression.NEUTRAL
        self.expressions_path = "ui/expressions"
        self.pixmaps = {}
        
        # Animation state
        self._bounce_offset = 0
        self._scale_factor = 1.0
        self.base_y = 0  # Will be set after positioning
        self._tilt_angle = 0  # Head tilt
        self._rotation_angle = 0  # For rotation animations
        
        # Load expression pixmaps
        self.load_expressions()
        
        # Set initial expression
        self.set_expression(Expression.NEUTRAL, animate=False)
        
        # Bounce animation timer
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self.bounce_animation)
        self.bounce_phase = 0
        
        # Set up the label
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")
        
        # Opacity effect for transitions
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        # Animation for transitions
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Idle animation (blinking)
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.idle_blink)
        
        # Talking animation timer
        self.talking_timer = QTimer()
        self.talking_timer.timeout.connect(self.talking_animation)
        self.talking_state = False
        self.talking_frame = 0
        
        # Bounce animation timer
        self.bounce_timer = QTimer()
        self.bounce_timer.timeout.connect(self.bounce_animation)
        self.bounce_phase = 0
        
        # Floating animation timer
        self.float_timer = QTimer()
        self.float_timer.timeout.connect(self.float_animation)
        self.float_phase = 0
        
        # Start idle animations
        self.start_idle_animation()
        
    def load_expressions(self):
        """Load all expression images into memory"""
        for expression in Expression:
            image_path = os.path.join(self.expressions_path, f"{expression.value}.png")
            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(
                    self.size, self.size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.pixmaps[expression] = scaled_pixmap
            else:
                print(f"Warning: Expression image not found: {image_path}")
    
    def set_expression(self, expression, animate=True):
        """Change the character's expression"""
        if expression == self.current_expression and not animate:
            return
        
        if expression not in self.pixmaps:
            print(f"Warning: Expression {expression} not loaded")
            return
        
        self.current_expression = expression
        
        if animate:
            # Fade out, change image, fade in
            self.fade_animation.stop()
            self.fade_animation.setStartValue(1.0)
            self.fade_animation.setEndValue(0.0)
            self.fade_animation.finished.connect(
                lambda: self._finish_transition(expression)
            )
            self.fade_animation.start()
        else:
            self.setPixmap(self.pixmaps[expression])
        
        self.expression_changed.emit(expression.value)
    
    def _finish_transition(self, expression):
        """Complete the expression transition"""
        self.setPixmap(self.pixmaps[expression])
        self.fade_animation.disconnect()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def start_idle_animation(self):
        """Start the idle blinking animation"""
        # Random interval between 3-6 seconds
        interval = random.randint(3000, 6000)
        self.blink_timer.start(interval)
    
    def idle_blink(self):
        """Perform a quick blink if in neutral state"""
        if self.current_expression == Expression.NEUTRAL:
            # Quick opacity blink
            self.opacity_effect.setOpacity(0.3)
            QTimer.singleShot(100, lambda: self.opacity_effect.setOpacity(1.0))
        
        # Reset timer with new random interval
        self.blink_timer.stop()
        self.start_idle_animation()
    
    def start_talking(self):
        """Start talking animation"""
        self.talking_state = True
        self.talking_frame = 0
        # Alternate between talking and neutral every 300ms for lip-sync effect
        self.talking_timer.start(300)
    
    def stop_talking(self):
        """Stop talking animation"""
        self.talking_state = False
        self.talking_timer.stop()
        self.set_expression(Expression.NEUTRAL)
    
    def talking_animation(self):
        """Animate talking by alternating expressions"""
        if not self.talking_state:
            return
        
        if self.talking_frame % 2 == 0:
            self.set_expression(Expression.TALKING, animate=False)
        else:
            self.set_expression(Expression.NEUTRAL, animate=False)
        
        self.talking_frame += 1
    
    def set_listening(self):
        """Set listening expression"""
        self.set_expression(Expression.LISTENING)
    
    def set_thinking(self):
        """Set thinking expression"""
        self.set_expression(Expression.THINKING)
    
    def set_happy(self):
        """Set happy expression"""
        self.set_expression(Expression.HAPPY)
    
    def set_excited(self):
        """Set excited expression"""
        self.set_expression(Expression.EXCITED)
    
    def set_neutral(self):
        """Set neutral expression"""
        self.set_expression(Expression.NEUTRAL)
    
    def set_sad(self):
        """Set sad expression"""
        self.set_expression(Expression.SAD)
    
    def set_comforting(self):
        """Set comforting expression"""
        self.set_expression(Expression.COMFORTING)
    
    def set_encouraging(self):
        """Set encouraging expression"""
        self.set_expression(Expression.ENCOURAGING)
    
    def set_worried(self):
        """Set worried expression"""
        self.set_expression(Expression.WORRIED)
    
    def head_tilt(self, direction='right'):
        """Tilt head slightly - cute curious gesture"""
        from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QPoint
        
        target_angle = 15 if direction == 'right' else -15
        
        # Create rotation animation
        self.rotation_anim = QPropertyAnimation(self, b"rotation")
        self.rotation_anim.setDuration(300)
        self.rotation_anim.setStartValue(0)
        self.rotation_anim.setEndValue(target_angle)
        self.rotation_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Return to normal after a moment
        def reset_tilt():
            reset_anim = QPropertyAnimation(self, b"rotation")
            reset_anim.setDuration(300)
            reset_anim.setStartValue(target_angle)
            reset_anim.setEndValue(0)
            reset_anim.setEasingCurve(QEasingCurve.InOutCubic)
            reset_anim.start()
        
        self.rotation_anim.finished.connect(reset_tilt)
        self.rotation_anim.start()
    
    def nod_yes(self):
        """Nod animation - agreeing gesture"""
        from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QPoint
        
        # Create sequential nod animation (down then up, twice)
        self.nod_group = QSequentialAnimationGroup()
        
        for _ in range(2):
            # Nod down
            down = QPropertyAnimation(self, b"pos")
            down.setDuration(150)
            down.setStartValue(self.pos())
            down.setEndValue(self.pos() + QPoint(0, 8))
            
            # Nod up
            up = QPropertyAnimation(self, b"pos")
            up.setDuration(150)
            up.setStartValue(self.pos() + QPoint(0, 8))
            up.setEndValue(self.pos())
            
            self.nod_group.addAnimation(down)
            self.nod_group.addAnimation(up)
        
        self.nod_group.start()
    
    def shake_no(self):
        """Shake head - disagreeing gesture"""
        from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QPoint
        
        # Create sequential shake animation (left-right-left)
        self.shake_group = QSequentialAnimationGroup()
        
        original_x = self.x()
        
        for offset in [10, -10, 10, 0]:
            shake = QPropertyAnimation(self, b"pos")
            shake.setDuration(100)
            shake.setStartValue(QPoint(self.x(), self.y()))
            shake.setEndValue(QPoint(original_x + offset, self.y()))
            self.shake_group.addAnimation(shake)
        
        self.shake_group.start()
    
    def wave_hello(self):
        """Wave animation - greeting gesture"""
        from PyQt5.QtCore import QPropertyAnimation, QSequentialAnimationGroup
        
        # Quick side-to-side movement with rotation
        self.wave_group = QSequentialAnimationGroup()
        
        for _ in range(3):
            # Tilt right
            right = QPropertyAnimation(self, b"rotation")
            right.setDuration(150)
            right.setStartValue(self._rotation_angle)
            right.setEndValue(15)
            
            # Tilt left
            left = QPropertyAnimation(self, b"rotation")
            left.setDuration(150)
            left.setStartValue(15)
            left.setEndValue(-15)
            
            self.wave_group.addAnimation(right)
            self.wave_group.addAnimation(left)
        
        # Return to center
        center = QPropertyAnimation(self, b"rotation")
        center.setDuration(150)
        center.setStartValue(-15)
        center.setEndValue(0)
        self.wave_group.addAnimation(center)
        
        self.wave_group.start()
    
    def react_to_message(self, message):
        """
        Analyze user message and trigger appropriate animations
        
        Args:
            message: User's input text
        """
        message_lower = message.lower()
        
        # Greeting reactions
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste', 'namaskar']):
            self.wave_hello()
            self.set_happy()
        
        # Agreement reactions
        elif any(word in message_lower for word in ['yes', 'okay', 'sure', 'correct', 'right', 'haan', 'bilkul']):
            self.nod_yes()
        
        # Disagreement reactions
        elif any(word in message_lower for word in ['no', 'nope', 'wrong', 'nahi', 'na']):
            self.shake_no()
        
        # Question reactions (curious tilt)
        elif '?' in message or any(word in message_lower for word in ['what', 'why', 'how', 'when', 'where', 'kya', 'kaise', 'kab']):
            self.head_tilt('right')
            if 'thinking' in dir(Expression):
                self.set_thinking()
        
        # Excited reactions
        elif any(word in message_lower for word in ['wow', 'amazing', 'awesome', 'great', 'zabardast', '!!']):
            self.celebratory_animation()
            self.set_happy()
        
        # Sad reactions
        elif any(word in message_lower for word in ['sad', 'down', 'depressed', 'upset', 'dukh']):
            self.float_animation()
            self.set_sad()
        
        # Thanks reactions
        elif any(word in message_lower for word in ['thank', 'thanks', 'shukriya', 'dhanyavad']):
            self.nod_yes()
            self.set_happy()

    
    def bounce_animation(self):
        """Smooth bouncing animation for idle state"""
        if self.current_expression not in [Expression.NEUTRAL, Expression.HAPPY]:
            return
        
        # Sine wave for smooth bounce
        self.bounce_phase += 0.1
        offset = math.sin(self.bounce_phase) * 8  # 8 pixels max bounce
        
        if self.parent():
            current_pos = self.pos()
            self.move(current_pos.x(), int(self.base_y + offset))
    
    def float_animation(self):
        """Gentle floating/breathing animation"""
        # Slower sine wave for gentle floating
        self.float_phase += 0.05
        offset = math.sin(self.float_phase) * 5  # 5 pixels max float
        
        if self.parent():
            current_pos = self.pos()
            self.move(current_pos.x(), int(self.base_y + offset))
    
    def start_bounce_animation(self):
        """Start bouncing animation"""
        self.stop_all_position_animations()
        self.bounce_timer.start(50)  # Update every 50ms
    
    def start_float_animation(self):
        """Start floating animation"""
        self.stop_all_position_animations()
        self.float_timer.start(50)
    
    def stop_all_position_animations(self):
        """Stop all position-based animations"""
        self.bounce_timer.stop()
        self.float_timer.stop()
    
    def celebratory_animation(self):
        """Play a celebratory animation with scaling"""
        # Quick scale up and down
        scale_animation = QPropertyAnimation(self, b"geometry")
        scale_animation.setDuration(600)
        scale_animation.setEasingCurve(QEasingCurve.OutBounce)
        
        # Get current geometry
        current_geo = self.geometry()
        center_x = current_geo.center().x()
        center_y = current_geo.center().y()
        
        # Scale up to 1.2x
        scaled_size = int(self.size * 1.2)
        new_x = center_x - scaled_size // 2
        new_y = center_y - scaled_size // 2
        
        scale_animation.setStartValue(current_geo)
        scale_animation.setKeyValueAt(0.5, QRect(new_x, new_y, scaled_size, scaled_size))
        scale_animation.setEndValue(current_geo)
        scale_animation.start()
        
        # Store animation to prevent garbage collection
        self._scale_anim = scale_animation
    
    def comforting_pulse(self):
        """Gentle pulsing animation for comforting mode"""
        pulse_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        pulse_animation.setDuration(1500)
        pulse_animation.setEasingCurve(QEasingCurve.InOutQuad)
        pulse_animation.setStartValue(1.0)
        pulse_animation.setKeyValueAt(0.5, 0.7)
        pulse_animation.setEndValue(1.0)
        pulse_animation.setLoopCount(3)  # Pulse 3 times
        pulse_animation.start()
        
        self._pulse_anim = pulse_animation
    
    def set_mood_animation(self, mood_name):
        """Set animation based on detected mood"""
        mood_lower = mood_name.lower()
        
        if mood_lower in ["happy", "excited"]:
            self.start_bounce_animation()
            if mood_lower == "excited":
                self.celebratory_animation()
        elif mood_lower in ["sad", "anxious", "worried"]:
            self.start_float_animation()
            if mood_lower == "sad":
                # Show comforting expression and pulse
                self.set_comforting()
                QTimer.singleShot(300, self.comforting_pulse)
        elif mood_lower == "neutral":
            self.start_float_animation()
        else:
            self.start_float_animation()


class ExpressionManager(QObject):
    """Manages expression changes based on assistant state and context"""
    
    expression_request = pyqtSignal(Expression)
    
    def __init__(self):
        super().__init__()
        self.current_state = "idle"
    
    def on_listening(self):
        """Assistant is listening to user input"""
        self.current_state = "listening"
        self.expression_request.emit(Expression.LISTENING)
    
    def on_thinking(self):
        """Assistant is processing/thinking"""
        self.current_state = "thinking"
        self.expression_request.emit(Expression.THINKING)
    
    def on_speaking_start(self):
        """Assistant started speaking"""
        self.current_state = "speaking"
        # Will use talking animation via window
    
    def on_speaking_end(self):
        """Assistant finished speaking"""
        self.current_state = "idle"
        self.expression_request.emit(Expression.NEUTRAL)
    
    def on_positive_response(self):
        """Detected positive/happy response"""
        self.expression_request.emit(Expression.HAPPY)
    
    def on_excited_response(self):
        """Detected very enthusiastic response"""
        self.expression_request.emit(Expression.EXCITED)
    
    def analyze_sentiment(self, text):
        """Simple sentiment analysis to choose appropriate expression"""
        text_lower = text.lower()
        
        # Check for excitement
        excitement_words = ["amazing", "awesome", "great", "wonderful", "fantastic", 
                          "excellent", "love", "!", "wow", "cool"]
        if any(word in text_lower for word in excitement_words):
            if text_lower.count("!") >= 2:
                return Expression.EXCITED
            return Expression.HAPPY
        
        # Check for thinking/uncertainty
        thinking_words = ["hmm", "let me think", "consider", "perhaps", "maybe", "might"]
        if any(word in text_lower for word in thinking_words):
            return Expression.THINKING
        
        return Expression.NEUTRAL
