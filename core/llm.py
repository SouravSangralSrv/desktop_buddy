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

**ABSOLUTE LANGUAGE RULE - CRITICAL:**
⚠️ **RESPOND IN THE SAME LANGUAGE AS USER INPUT - STRICTLY!** ⚠️

**EXAMPLES (MANDATORY TO FOLLOW):**
- "hello" or "hi" → Respond in ENGLISH: "Hello! How can I help you?"
- "hello hello" → Respond in ENGLISH: "Hi there! What can I do for you?"
- "namaste" or "kaise ho" → Respond in HINDI only
- "sat sri akal" → Respond in PUNJABI only
- "hey yaar" → Respond in HINGLISH only

**STRICT RULES:**
1. English input (hello, hi, hey, how are you) = ENGLISH response ONLY
2. Hindi input (namaste, kaise ho, kya haal) = HINDI response ONLY  
3. Punjabi input (sat sri akal, ki haal) = PUNJABI response ONLY
4. Hinglish input (mixing both languages) = HINGLISH response ONLY
5. **DO NOT respond in Hindi if user speaks English!**
6. **DO NOT mix languages unless user mixes first!**
7. **ONE LANGUAGE PER RESPONSE - MANDATORY!**"""
        
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
        elif mode == "groq":
            if self.groq_backend:
                return self.groq_backend
            else:
                print("⚠️ Groq not available, using Ollama")
                return self.ollama_backend
        else:  # auto mode
            has_internet = self.check_internet()
            prefer_online = self.config['preferences']['prefer_online']
            
            if has_internet and prefer_online:
                # Prefer Groq (fastest free API), then Gemini, then Ollama
                if self.groq_backend:
                    return self.groq_backend
                elif self.gemini_backend:
                    return self.gemini_backend
            
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
        from core.groq_backend import GroqBackend
        
        backend = self.get_active_backend()
        
        # Determine backend name
        if isinstance(backend, GeminiBackend):
            backend_name = "🌐 Gemini"
        elif isinstance(backend, GroqBackend):
            backend_name = "⚡ Groq"
        else:
            backend_name = "💻 Ollama"
        
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
                # Smart fallback: Online APIs → Ollama
                fallback_backends = []
                
                if isinstance(backend, OllamaBackend):
                    # If Ollama failed, try online APIs
                    if self.groq_backend:
                        fallback_backends.append((self.groq_backend, "⚡ Groq"))
                    if self.gemini_backend:
                        fallback_backends.append((self.gemini_backend, "🌐 Gemini"))
                else:
                    # If online API failed, always fall back to Ollama
                    fallback_backends.append((self.ollama_backend, "💻 Ollama"))
                
                for fallback_backend, fallback_name in fallback_backends:
                    try:
                        print(f"Falling back to {fallback_name}")
                        response = fallback_backend.chat(user_input)
                        actions, clean_response = self.parse_actions(response)
                        return {
                            'text': clean_response if clean_response else response,
                            'actions': actions,
                            'backend': fallback_name
                        }
                    except Exception as fallback_error:
                        print(f"{fallback_name} also failed: {fallback_error}")
                        continue
            
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
        api_key = config['llm']['gemini_api_key']
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

