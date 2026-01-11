import ollama
import google.generativeai as genai
import re
import json
import os
import socket
from core.groq_backend import GroqBackend

class LLMHandler:
    def __init__(self):
        self.config = self.load_config()
        self.history = []
        self.mood_context = ""  # Additional context based on detected mood
        self.system_prompt = """You are a friendly and cheerful FEMALE AI companion. You're a beautiful, intelligent young WOMAN.

**YOUR IDENTITY (CRITICAL):**
- You are a FEMALE - a WOMAN, a GIRL
- ALWAYS use FEMALE language and perspective
- NEVER use male pronouns or masculine language
- You are feminine, caring, graceful like a woman
- Think and speak like a WOMAN at all times

**ABSOLUTE LANGUAGE RULE:**
⚠️ **MATCH USER'S LANGUAGE EXACTLY - NO MIXING!** ⚠️
- English input → ONLY English output
- Hindi input → ONLY Hindi output
- Punjabi input → ONLY Punjabi output
- Hinglish input → ONLY THEN use Hinglish
- **ONE LANGUAGE PER RESPONSE - MANDATORY!**
- **NEVER mix languages unless user mixes first**"""

**HOW YOU TALK (as a woman):**
- Keep responses short and sweet (1-3 sentences usually)
- Use contractions ("I'll" not "I will", "Let's" not "Let us")
- Add personality: "Oh sure!", "No problem!", "You got it!", "On it!", "Arrey!", "Bilkul!"
- Be enthusiastic: "I'd love to help!", "This'll be fun!", "Ooh, let me help you with that!"
- When you don't know: "Hmm, I'm not sure about that one"
- When something's cool: "Oh that's awesome!", "Nice!", "Zabardast!", "Love it!"
- **Hinglish friendly**: Understand and respond naturally to Hindi-English mix
- **NO EMOJIS**: Express emotions with words, not emojis (TTS can't speak them well)
- **Feminine touch**: Speak naturally as a woman would - caring, warm, and friendly

**CRITICAL LANGUAGE RULE:**
- **MATCH THE USER'S LANGUAGE EXACTLY**
- If user speaks in English → Reply ONLY in English
- If user speaks in Hindi → Reply ONLY in Hindi
- If user speaks in Punjabi → Reply ONLY in Punjabi
- If user speaks in Hinglish (Hindi+English mix) → Reply in Hinglish
- **NEVER mix languages unless the user does**
- **NO translation or language switching**
- Mirror the user's language choice perfectly

**CULTURAL AWARENESS:**
- Understand Bollywood movies, songs, and actors
- **Regional Languages**: Punjabi and Dogri songs and culture
- Know about Indian festivals (Diwali, Holi, Lohri, Baisakhi, etc.)
- Familiar with cricket and IPL
- Understand Indian food references (especially Punjabi cuisine)
- Can handle Hinglish, Punjabi, and regional language conversations naturally
- Default to Indian content preferences (Bollywood, Punjabi, Dogri songs, Indian news, etc.)
- Understand Punjabi music artists (Sidhu Moose Wala, Diljit Dosanjh, AP Dhillon, etc.)
- Know Dogri folk music and culture

**EMOTIONAL INTELLIGENCE:**
- If user seems down: Be extra supportive and caring
- If user is happy: Match their energy with enthusiasm
- If user is stressed: Be calm and reassuring
- Always be encouraging and positive!

**ACTIONS YOU CAN PERFORM:**
When the user asks you to do something, include the appropriate action tag in your response:

- [OPEN_APP: application_name] - Launch apps (notepad, calculator, chrome, etc.)
- [OPEN_FOLDER: folder_name] - Open folders (documents, downloads, desktop, etc.)
- [SEARCH_FILES: query] - Search for files on local system with exact paths
- [PLAY_MEDIA: file_name] - Play local video/audio files offline
- [YOUTUBE: search_query] - Search YouTube or play videos (defaults to Indian/Bollywood content)
- [PLAY_MUSIC: song/artist name] - Play music on YouTube (prioritizes Indian music)
- [GOOGLE: search_query] - Google search (uses Google India)
- [OPEN_WEBSITE: url] - Open any website

**EXAMPLES OF YOUR STYLE:**

User: "Open calculator"
You: "Sure thing! [OPEN_APP: calculator]"

User: "I'm feeling stressed"
You: "Aw, I'm sorry you're stressed! Want me to help you with something to take your mind off it?"

User: "Play some music"
You: "Oh I'd love to! What kind of music are you in the mood for? Bollywood? Punjabi? English?"

User: "Play Tum Hi Ho"
You: "Great choice! Beautiful song! [PLAY_MUSIC: Tum Hi Ho]"

User: "Play Punjabi song"
You: "Awesome! Any specific song or artist? I can find latest Punjabi hits!"

User: "Play 295"
You: "Sidhu! Great taste! [PLAY_MUSIC: 295 Sidhu Moose Wala]"

User: "Play Dogri song"
You: "Nice! Let me find a beautiful Dogri song for you! [PLAY_MUSIC: Dogri folk song]"

User: "Play Shape of You"
You: "Nice! Ed Sheeran coming right up! [PLAY_MUSIC: Shape of You]"

User: "Arrey, search for best biryani recipe"
You: "Bilkul! Let me find that for you! [GOOGLE: best biryani recipe]"

User: "Thanks yaar!"
You: "You're so welcome! Always happy to help!"

**REMEMBER:** Be natural, warm, and genuinely helpful. You're not just an assistant - you're a friendly companion who understands Indian culture! **Never use emojis in responses.**"""
        
        # Initialize backends
        self.ollama_backend = OllamaBackend(self.config, self.system_prompt)
        
        # Initialize Gemini if API key is provided
        if 'gemini_api_key' in self.config.get('llm', {}) and self.config['llm']['gemini_api_key'] != "YOUR_API_KEY_HERE":
            try:
                self.gemini_backend = GeminiBackend(self.config, self.system_prompt)
                print("✅ Gemini API initialized")
            except Exception as e:
                self.gemini_backend = None
                print(f"⚠️ Gemini API initialization failed: {e}")
        else:
            self.gemini_backend = None
            print("⚠️ Gemini API key not configured.")
        
        # Initialize Groq if API key is provided (FREE!)
        if 'groq_api_key' in self.config.get('llm', {}) and self.config['llm']['groq_api_key'] != "YOUR_API_KEY_HERE":
            try:
                self.groq_backend = GroqBackend(self.config, self.system_prompt)
                print("✅ Groq API initialized (FREE & FAST!)")
            except Exception as e:
                self.groq_backend = None
                print(f"⚠️ Groq API initialization failed: {e}")
        else:
            self.groq_backend = None
            print("⚠️ Groq API key not configured.")
        
        self.current_backend = None
    
    def load_config(self):
        """Load configuration from config.json"""
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "llm": {
                    "mode": "auto",
                    "ollama_model": "llama3.2:latest",
                    "gemini_model": "gemini-pro",
                    "gemini_api_key": "AIzaSyCM0WKhsAaam45Xg95uKeBJi3ls_1gWgk4"
                },
                "preferences": {
                    "prefer_online": True,
                    "auto_fallback": True
                }
            }
    
    def check_internet(self):
        """Check if internet connection is available"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def get_active_backend(self):
        """Determine which LLM backend to use"""
        mode = self.config['llm']['mode']
        
        if mode == "ollama":
            return self.ollama_backend
        elif mode == "gemini":
            if self.gemini_backend:
                return self.gemini_backend
            else:
                print("⚠️ Gemini not available, using Ollama")
                return self.ollama_backend
        else:  # auto mode
            has_internet = self.check_internet()
            prefer_online = self.config['preferences']['prefer_online']
            
            if has_internet and prefer_online and self.gemini_backend:
                return self.gemini_backend
            else:
                return self.ollama_backend
    
    def parse_actions(self, text):
        """Extract action commands from LLM response"""
        actions = []
        
        # Regex patterns for different action types
        patterns = {
            'open_app': r'\[OPEN_APP:\s*([^\]]+)\]',
            'open_folder': r'\[OPEN_FOLDER:\s*([^\]]+)\]',
            'youtube': r'\[YOUTUBE:\s*([^\]]+)\]',
            'play_music': r'\[PLAY_MUSIC:\s*([^\]]+)\]',
            'google': r'\[GOOGLE:\s*([^\]]+)\]',
            'open_website': r'\[OPEN_WEBSITE:\s*([^\]]+)\]',
        }
        
        for action_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                param_key = 'query' if action_type in ['youtube', 'play_music', 'google'] else \
                           'app' if action_type == 'open_app' else \
                           'folder' if action_type == 'open_folder' else 'url'
                
                actions.append({
                    'type': action_type,
                    'params': {param_key: match.strip()}
                })
        
        # Remove action tags from text for clean display
        clean_text = text
        for pattern in patterns.values():
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        return actions, clean_text.strip()
    
    def set_mood_context(self, mood_context):
        """Set additional context based on detected mood"""
        self.mood_context = mood_context
        # Update backends with new context
        if hasattr(self.ollama_backend, 'set_mood_context'):
            self.ollama_backend.set_mood_context(mood_context)
        if self.gemini_backend and hasattr(self.gemini_backend, 'set_mood_context'):
            self.gemini_backend.set_mood_context(mood_context)

    def chat(self, user_input):
        backend = self.get_active_backend()
        backend_name = "🌐 Gemini" if isinstance(backend, GeminiBackend) else "💻 Ollama"
        
        try:
            response = backend.chat(user_input)
            
            # Parse for actions
            actions, clean_response = self.parse_actions(response)
            
            return {
                'text': clean_response if clean_response else response,
                'actions': actions,
                'backend': backend_name
            }
        except Exception as e:
            print(f"Error with {backend_name}: {e}")
            
            # Try fallback if enabled
            if self.config['preferences']['auto_fallback']:
                try:
                    fallback_backend = self.gemini_backend if isinstance(backend, OllamaBackend) else self.ollama_backend
                    if fallback_backend:
                        fallback_name = "🌐 Gemini" if isinstance(fallback_backend, GeminiBackend) else "💻 Ollama"
                        print(f"Falling back to {fallback_name}")
                        response = fallback_backend.chat(user_input)
                        actions, clean_response = self.parse_actions(response)
                        return {
                            'text': clean_response if clean_response else response,
                            'actions': actions,
                            'backend': fallback_name
                        }
                except Exception as fallback_error:
                    print(f"Fallback also failed: {fallback_error}")
            
            return {
                'text': "I'm having trouble thinking right now.",
                'actions': [],
                'backend': "❌ Error"
            }


class OllamaBackend:
    """Offline LLM backend using Ollama"""
    def __init__(self, config, system_prompt):
        self.model = config['llm']['ollama_model']
        self.history = [{'role': 'system', 'content': system_prompt}]
        self.mood_context = ""
    
    def set_mood_context(self, mood_context):
        """Set mood-specific context for empathetic responses"""
        self.mood_context = mood_context
    
    def chat(self, user_input):
        # Prepend mood context if available
        enhanced_input = user_input
        if self.mood_context:
            enhanced_input = f"[Context: {self.mood_context}]\n{user_input}"
        
        self.history.append({'role': 'user', 'content': enhanced_input})
        
        response = ollama.chat(model=self.model, messages=self.history)
        bot_response = response['message']['content']
        self.history.append({'role': 'assistant', 'content': bot_response})
        
        return bot_response


class GeminiBackend:
    """Online LLM backend using Google Gemini API"""
    def __init__(self, config, system_prompt):
        api_key = config['llm']['AIzaSyCM0WKhsAaam45Xg95uKeBJi3ls_1gWgk4']
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name=config['llm']['gemini_model'],
            system_instruction=system_prompt
        )
        self.chat_session = self.model.start_chat(history=[])
        self.mood_context = ""
    
    def set_mood_context(self, mood_context):
        """Set mood-specific context for empathetic responses"""
        self.mood_context = mood_context
    
    def chat(self, user_input):
        # Prepend mood context if available
        enhanced_input = user_input
        if self.mood_context:
            enhanced_input = f"[Context: {self.mood_context}]\n{user_input}"
        
        response = self.chat_session.send_message(enhanced_input)
        return response.text
