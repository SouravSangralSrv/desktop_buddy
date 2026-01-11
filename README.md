# 🤖 Desktop Buddy

> Your AI-powered desktop companion with personality! Chat, get help, and have fun with an animated character.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/platform-windows-0078d4.svg)](https://www.microsoft.com/windows)

![Desktop Buddy Demo](https://via.placeholder.com/800x400?text=Desktop+Buddy+Screenshot)

---

## ✨ Features

- 🎭 **Animated Character** - 6 expressions with smooth animations (happy, thinking, listening, talking, excited, neutral)
- 💬 **Multi-Modal Chat** - Voice input and text chat
- 🧠 **Multiple AI Backends**:
  - ⚡ **Groq** (Free & Fast - Recommended!)
  - 🌐 **Google Gemini** (High Quality)
  - 💻 **Ollama** (Local/Offline - Privacy First)
  - 🔄 Auto-detection of installed Ollama models (DeepSeek, Llama3, Phi3, Mistral, etc.)
- 🎯 **System Actions** - Open apps, search Google, play YouTube videos
- 🎨 **Mood Detection** - Analyzes sentiment and responds empathetically
- 🌍 **Multi-Language** - Auto-detects language (English, Hindi, Hinglish supported)
- 📦 **Standalone Executable** - No Python required for end users

---

## 🚀 Quick Start

### For Users (Download .exe)

1. **Download** `DesktopBuddy.exe` from [Releases](../../releases)
2. **Run** the executable
3. **Setup Wizard** will guide you through:
   - Choose AI backend (Groq is free!)
   - Enter API key (or select local Ollama)
   - Select voice preferences
4. **Start chatting!**

### For Developers (Run from Source)

```bash
# Clone repository
git clone https://github.com/yourusername/desktop-buddy.git
cd desktop-buddy

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

---

## ⚙️ Configuration

### Getting API Keys

#### Groq (Recommended - Free!)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create API key
4. Use in setup wizard

#### Google Gemini
1. Visit [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Create API key
3. Use in setup wizard

#### Ollama (Local/Offline)
1. Download from [ollama.ai](https://ollama.ai)
2. Install and run `ollama serve`
3. Pull a model: `ollama pull llama3.2`
4. **Desktop Buddy auto-detects** all installed models!

### Supported Ollama Models

Desktop Buddy works with **ANY** Ollama model:
- `llama3.2:latest` - Fast, recommended
- `deepseek-r1:latest` - DeepSeek reasoning model
- `llama3.1:latest` - Larger, higher quality
- `phi3:latest` - Microsoft's efficient model
- `mistral:latest` - Mistral AI
- `gemma2:latest` - Google Gemma
- ...and any other Ollama model!

The setup wizard automatically detects and lists all your installed models.

---

## 🎮 Usage

### Voice Commands
- **Say anything** - Desktop Buddy listens and responds
- **"Open calculator"** - Opens Windows Calculator
- **"Search for Python tutorials"** - Google search
- **"Play Bohemian Rhapsody"** - YouTube search
- **"Goodbye"** - Exits the application

### Text Chat
- Type in the input box
- Press Enter or click Send
- Character animates with each response

### Switching Backends
Click the backend indicator to cycle through:
- 🔄 **Auto** (smart selection)
- 💻 **Ollama** (offline)
- 🌐 **Gemini** (Google)
- ⚡ **Groq** (fast & free)

---

## 🛠️ Building from Source

### Create Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
build.bat

# Output: dist\DesktopBuddy.exe
```

---

## 📁 Project Structure

```
desktop-buddy/
├── main.py                 # Application entry point
├── setup_wizard.py         # First-run setup wizard
├── core/
│   ├── llm.py             # LLM backend manager
│   ├── ollama_utils.py    # Ollama model detection
│   ├── groq_backend.py    # Groq API integration
│   ├── stt.py             # Speech-to-text
│   ├── tts.py             # Text-to-speech
│   ├── actions.py         # System actions
│   └── sentiment.py       # Mood detection
├── ui/
│   ├── window.py          # Main UI window
│   └── character.py       # Animated character
├── build.bat              # Build script
├── DesktopBuddy.spec      # PyInstaller config
├── INSTALL.md             # User installation guide
└── TROUBLESHOOTING.md     # Support guide
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [Groq](https://groq.com) - Fast inference API
- [Google Gemini](https://ai.google.dev/) - Powerful AI model
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - UI framework
- [Edge TTS](https://github.com/rany2/edge-tts) - Text-to-speech

---

## 💡 Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: See [INSTALL.md](INSTALL.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Discussions**: [GitHub Discussions](../../discussions)

---

**Enjoy your AI companion!** 🎉

Made with ❤️ using Python and AI
