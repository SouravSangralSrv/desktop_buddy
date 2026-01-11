"""
Sentiment Analysis Module for Desktop Buddy
Analyzes user input to detect emotional state and mood.
"""

from textblob import TextBlob
from enum import Enum


class Mood(Enum):
    """User mood categories"""
    HAPPY = "happy"
    SAD = "sad"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"


class SentimentAnalyzer:
    """Analyzes text for emotional content and user mood"""
    
    def __init__(self, sensitivity=0.5):
        """
        Initialize sentiment analyzer
        
        Args:
            sensitivity: Threshold for emotion detection (0-1), higher = more sensitive
        """
        self.sensitivity = sensitivity
        
        # Emotion keyword dictionaries
        self.emotion_keywords = {
            Mood.SAD: [
                "sad", "depressed", "down", "unhappy", "miserable", "upset",
                "crying", "tears", "lonely", "heartbroken", "disappointed",
                "hopeless", "gloomy", "melancholy", "blue", "dejected",
                "terrible", "awful", "horrible", "bad day", "feeling down"
            ],
            Mood.ANXIOUS: [
                "anxious", "worried", "stressed", "nervous", "scared", "afraid",
                "panic", "fear", "overwhelming", "concerned", "tense", "uneasy",
                "restless", "frightened", "terrified", "paranoid", "stressed out"
            ],
            Mood.ANGRY: [
                "angry", "mad", "furious", "annoyed", "irritated", "frustrated",
                "rage", "hate", "pissed", "livid", "outraged", "infuriated",
                "disgusted", "resentful", "bitter", "hostile"
            ],
            Mood.HAPPY: [
                "happy", "glad", "joyful", "pleased", "delighted", "cheerful",
                "content", "satisfied", "grateful", "blessed", "good", "great",
                "wonderful", "nice", "fine", "better", "positive", "smile", "smiling"
            ],
            Mood.EXCITED: [
                "excited", "thrilled", "amazing", "awesome", "fantastic",
                "incredible", "love", "excellent", "brilliant", "spectacular",
                "wonderful", "elated", "ecstatic", "pumped", "energized",
                "can't wait", "looking forward"
            ]
        }
    
    def analyze(self, text):
        """
        Analyze text for sentiment and emotion
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict with keys:
                - mood: Detected Mood enum
                - polarity: Sentiment score from -1 (negative) to 1 (positive)
                - subjectivity: How subjective the text is (0-1)
                - intensity: How strong the emotion is (0-1)
                - confidence: Confidence in the mood detection (0-1)
        """
        if not text or not text.strip():
            return {
                "mood": Mood.NEUTRAL,
                "polarity": 0.0,
                "subjectivity": 0.0,
                "intensity": 0.0,
                "confidence": 0.0
            }
        
        # Get TextBlob sentiment
        blob = TextBlob(text.lower())
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Detect mood using keywords
        mood, keyword_confidence = self._detect_mood_keywords(text.lower())
        
        # Calculate intensity based on polarity magnitude and subjectivity
        intensity = abs(polarity) * subjectivity
        
        # If no strong keywords, use polarity to determine mood
        if keyword_confidence < self.sensitivity:
            if polarity > 0.3:
                mood = Mood.HAPPY
                keyword_confidence = polarity * 0.7
            elif polarity < -0.3:
                mood = Mood.SAD
                keyword_confidence = abs(polarity) * 0.7
            else:
                mood = Mood.NEUTRAL
                keyword_confidence = 0.5
        
        return {
            "mood": mood,
            "polarity": polarity,
            "subjectivity": subjectivity,
            "intensity": intensity,
            "confidence": keyword_confidence
        }
    
    def _detect_mood_keywords(self, text):
        """
        Detect mood based on keyword matching
        
        Returns:
            tuple: (Mood, confidence_score)
        """
        mood_scores = {mood: 0 for mood in Mood}
        
        # Count keyword matches for each mood
        words = text.split()
        total_words = len(words)
        
        for mood, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                # Check for exact word match or phrase match
                if keyword in text:
                    # Give more weight to exact word matches
                    if f" {keyword} " in f" {text} ":
                        mood_scores[mood] += 2
                    else:
                        mood_scores[mood] += 1
        
        # Find mood with highest score
        if not any(mood_scores.values()):
            return Mood.NEUTRAL, 0.0
        
        best_mood = max(mood_scores, key=mood_scores.get)
        best_score = mood_scores[best_mood]
        
        # Calculate confidence based on keyword density
        confidence = min(1.0, best_score / max(3, total_words * 0.3))
        
        return best_mood, confidence
    
    def is_negative_mood(self, mood):
        """Check if mood is negative (sad, anxious, angry)"""
        return mood in [Mood.SAD, Mood.ANXIOUS, Mood.ANGRY]
    
    def is_positive_mood(self, mood):
        """Check if mood is positive (happy, excited)"""
        return mood in [Mood.HAPPY, Mood.EXCITED]
    
    def get_mood_description(self, mood):
        """Get a friendly description of the mood"""
        descriptions = {
            Mood.HAPPY: "You seem happy! 😊",
            Mood.SAD: "You seem down 😔",
            Mood.ANXIOUS: "You seem worried 😰",
            Mood.ANGRY: "You seem upset 😠",
            Mood.NEUTRAL: "Neutral mood 😐",
            Mood.EXCITED: "You seem excited! 🎉"
        }
        return descriptions.get(mood, "Unknown mood")
    
    def get_empathetic_context(self, analysis):
        """
        Generate context for LLM to respond empathetically
        
        Args:
            analysis: Result from analyze() method
            
        Returns:
            str: Context string to add to LLM prompt
        """
        mood = analysis["mood"]
        intensity = analysis["intensity"]
        
        if self.is_negative_mood(mood):
            if mood == Mood.SAD:
                if intensity > 0.6:
                    return "The user seems very sad or upset. Be extra supportive, empathetic, and try to cheer them up gently. Offer comfort and encouragement."
                else:
                    return "The user seems a bit down. Be supportive and friendly. Try to lift their spirits."
            elif mood == Mood.ANXIOUS:
                if intensity > 0.6:
                    return "The user seems very anxious or worried. Be calm, reassuring, and supportive. Help them feel safe and understood."
                else:
                    return "The user seems somewhat worried. Be reassuring and provide calm, helpful responses."
            elif mood == Mood.ANGRY:
                return "The user seems frustrated or upset. Be understanding, patient, and avoid being dismissive. Acknowledge their feelings."
        
        elif self.is_positive_mood(mood):
            if mood == Mood.EXCITED:
                return "The user seems very excited! Match their energy with enthusiasm and positivity!"
            elif mood == Mood.HAPPY:
                return "The user seems happy! Be cheerful and maintain the positive mood."
        
        return ""  # Neutral - no special context needed
