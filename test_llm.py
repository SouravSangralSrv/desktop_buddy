"""
Quick diagnostic script to test LLM backends
"""
import sys
from core.llm import LLMHandler

def test_llm():
    print("=" * 50)
    print("Testing LLM Backends")
    print("=" * 50)
    
    try:
        llm = LLMHandler()
        print("\n✅ LLM Handler initialized successfully")
        
        # Test with simple input
        test_input = "hello"
        print(f"\n📝 Testing with input: '{test_input}'")
        print("⏳ Waiting for response...")
        
        result = llm.chat(test_input)
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS!")
        print("=" * 50)
        print(f"Backend: {result['backend']}")
        print(f"Response: {result['text']}")
        print(f"Actions: {result['actions']}")
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ ERROR!")
        print("=" * 50)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        
        print("\n💡 Troubleshooting tips:")
        print("1. Check if Groq API key is valid in config.json")
        print("2. Check your internet connection")
        print("3. Try switching to Ollama mode in config.json")
        print("4. Make sure Ollama is running if using offline mode")

if __name__ == "__main__":
    test_llm()
