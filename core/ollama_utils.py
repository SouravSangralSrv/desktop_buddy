"""
Ollama Model Detection Utility
Detects installed Ollama models and provides selection UI
"""
import subprocess
import json
from typing import List, Dict, Optional


def get_installed_ollama_models() -> List[Dict[str, str]]:
    """
    Get list of installed Ollama models
    
    Returns:
        List of dicts with 'name' and 'size' keys
        Empty list if Ollama not installed or no models
    """
    try:
        # Run ollama list command
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("⚠️ Ollama not found or not running")
            return []
        
        # Parse output
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:  # No models (only header)
            return []
        
        models = []
        for line in lines[1:]:  # Skip header
            parts = line.split()
            if len(parts) >= 2:
                model_name = parts[0]
                # Extract just the model name without :tag if present
                base_name = model_name.split(':')[0]
                models.append({
                    'name': model_name,
                    'display_name': model_name,
                    'base_name': base_name
                })
        
        return models
    
    except FileNotFoundError:
        print("⚠️ Ollama not installed")
        return []
    except subprocess.TimeoutExpired:
        print("⚠️ Ollama command timeout")
        return []
    except Exception as e:
        print(f"⚠️ Error detecting Ollama models: {e}")
        return []


def is_ollama_running() -> bool:
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            timeout=3
        )
        return result.returncode == 0
    except:
        return False


def get_recommended_models() -> List[str]:
    """
    Get list of recommended Ollama models for Desktop Buddy
    These are known to work well with the application
    """
    return [
        "llama3.2:latest",      # Fast, good quality
        "llama3.1:latest",      # Larger, better quality
        "deepseek-r1:latest",   # DeepSeek reasoning model
        "phi3:latest",          # Microsoft's small model
        "mistral:latest",       # Mistral AI model
        "gemma2:latest",        # Google's Gemma model
    ]


def suggest_model_to_pull() -> str:
    """Suggest a good default model to pull"""
    return "llama3.2:latest"


def pull_ollama_model(model_name: str, progress_callback=None) -> bool:
    """
    Pull an Ollama model
    
    Args:
        model_name: Name of model to pull (e.g., "llama3.2:latest")
        progress_callback: Optional callback for progress updates
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if progress_callback:
            progress_callback(f"Pulling {model_name}...")
        
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Read output in real-time
        for line in process.stdout:
            if progress_callback:
                progress_callback(line.strip())
        
        process.wait()
        return process.returncode == 0
    
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False


if __name__ == '__main__':
    # Test the detection
    print("Testing Ollama Model Detection")
    print("=" * 50)
    
    if is_ollama_running():
        print("✅ Ollama is running")
        
        models = get_installed_ollama_models()
        if models:
            print(f"\n✅ Found {len(models)} installed model(s):")
            for model in models:
                print(f"  - {model['display_name']}")
        else:
            print("\n⚠️ No models installed")
            print(f"\nRecommended: {suggest_model_to_pull()}")
    else:
        print("❌ Ollama not running")
        print("\nTo install Ollama:")
        print("1. Download from https://ollama.ai")
        print("2. Install and run 'ollama serve'")
        print("3. Pull a model: ollama pull llama3.2")
