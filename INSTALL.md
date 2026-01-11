# Desktop Buddy - Installation Guide

Welcome to **Desktop Buddy**! Your AI-powered desktop companion. 🎉

## System Requirements

- **Operating System:** Windows 10 or Windows 11
- **Microphone:** Required for voice input
- **Internet:** Required for Groq/Gemini modes (optional for Ollama local mode)
- **Disk Space:** ~200MB for application

## Quick Start (For Users)

### Option 1: Download Executable (Easiest)

1. **Download** `DesktopBuddy.exe` from the releases page
2. **Double-click** to run
3. **First-time setup wizard** will guide you through configuration:
   - Choose AI backend (Groq recommended - it's free!)
   - Enter API key if using Groq or Gemini
   - Select voice preferences
4. **Click "Save & Start"** - Done! 🎉

### Option 2: Run from Source (For Developers)

```bash
# Clone repository
git clone <repository-url>
cd desktop_buddy

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Getting API Keys

### Groq (Recommended - Free & Fast!)

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to "API Keys" section
4. Create new API key
5. Copy the key (starts with `gsk_...`)
6. Paste into Desktop Buddy setup wizard

**Cost:** FREE! Generous free tier.

### Google Gemini (Optional)

1. Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create API key
4. Copy and use in Desktop Buddy

### Ollama (Local/Offline)

1. Download Ollama from [https://ollama.ai](https://ollama.ai)
2. Install Ollama
3. Run: `ollama pull llama3.2`
4. Keep Ollama running in background
5. Select "Ollama" mode in Desktop Buddy setup

## First Run

When you launch Desktop Buddy for the first time:

1. **Setup Wizard** appears automatically
2. **Choose backend:**
   - ⚡ **Groq** - Fast, free, recommended for most users
   - 🌐 **Gemini** - Google's AI, high quality
   - 💻 **Ollama** - Local, works offline
3. **Enter API key** (if using Groq/Gemini)
4. **Choose voice** preset
5. **Click "Save & Start"**

Desktop Buddy will remember your settings!

## Usage

- **Voice Mode:** Speak naturally, Desktop Buddy listens and responds
- **Text Mode:** Type in the chat window
- **Commands:** Ask to open apps, search YouTube, play music, etc.
- **Interrupt:** Start speaking to interrupt TTS playback

## Troubleshooting

### "Microphone not detected"
- Check Windows privacy settings
- Allow microphone access for Desktop Buddy
- Make sure microphone is plugged in and working

### "LLM not responding"
- **Groq mode:** Check API key is correct
- **Ollama mode:** Make sure Ollama is running (`ollama serve`)
- **Network:** Check internet connection for online modes

### "Voice not working"
- Edge TTS requires internet connection
- Check audio output device is working
- Try different voice preset in settings

### "API Key Invalid"
- Double-check you copied the complete key
- Make sure there are no extra spaces
- Regenerate key from console if needed

## Configuration

Edit `config.json` to customize:

```json
{
  "llm": {
    "mode": "groq",           // groq, gemini, or ollama
    "groq_api_key": "your_key_here"
  },
  "tts": {
    "voice_preset": "indian_english"  // Voice style
  }
}
```

## Support

- **Issues:** Report bugs on GitHub issues page
- **Questions:** Check the README.md for more details
- **Updates:** Check releases page for new versions

---

**Enjoy your AI companion!** 🎉
