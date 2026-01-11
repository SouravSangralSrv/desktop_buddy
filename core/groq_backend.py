# Add this at the end of core/llm.py after GeminiBackend class

class GroqBackend:
    """FREE & FAST LLM backend using Groq API"""
    def __init__(self, config, system_prompt):
        from groq import Groq
        
        api_key = config['llm']['groq_api_key']
        self.client = Groq(api_key=api_key)
        self.model = config['llm'].get('groq_model', 'llama-3.3-70b-versatile')  # Free fast model
        self.system_prompt = system_prompt
        self.history = []
        self.mood_context = ""
    
    def set_mood_context(self, mood_context):
        """Set mood-specific context for empathetic responses"""
        self.mood_context = mood_context
    
    def chat(self, user_input):
        # Prepend mood context if available
        enhanced_input = user_input
        if self.mood_context:
            enhanced_input = f"[Context: {self.mood_context}]\n{user_input}"
        
        # Build messages with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": enhanced_input})
        
        # Call Groq API (super fast!)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        bot_response = response.choices[0].message.content
        
        # Update history
        self.history.append({"role": "user", "content": enhanced_input})
        self.history.append({"role": "assistant", "content": bot_response})
        
        # Keep history manageable
        if len(self.history) > 20:
            self.history = self.history[-20:]
        
        return bot_response
