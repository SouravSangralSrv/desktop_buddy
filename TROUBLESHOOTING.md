# Desktop Buddy - Troubleshooting Guide

Common issues and their solutions.

## Installation Issues

### "Python not found" when running from source
**Solution:** Install Python 3.10 or later from [python.org](https://python.org)

### "pip install failed"
**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

---

## First Run Issues

### Setup wizard doesn't appear
**Solution:** Delete `config.json` and restart Desktop Buddy

### "Invalid API key" error
**Possible causes:**
1. API key copied incorrectly (check for spaces)
2. API key not activated yet (wait a few minutes)
3. Wrong API key service selected

**Solution:**
- For Groq: Get free key from [console.groq.com](https://console.groq.com)
- For Gemini: Get key from [makersuite.google.com](https://makersuite.google.com/app/apikey)
- Make sure you're using the right key for the right service

---

## Microphone Issues

### "No microphone detected"
**Windows Settings:**
1. Open Settings → Privacy → Microphone
2. Enable "Allow apps to access your microphone"
3. Make sure Desktop Buddy has microphone permission

### Microphone works but no recognition
**Solutions:**
1. **Check energy threshold:**
   - Console shows "Energy threshold set to X"
   - If too high (>4000), microphone might be too quiet
   - If too low (<300), picking up too much noise

2. **Test microphone:**
   ```bash
   # In Python, test with:
   import speech_recognition as sr
   r = sr.Recognizer()
   with sr.Microphone() as source:
       r.adjust_for_ambient_noise(source)
       print(f"Energy threshold: {r.energy_threshold}")
   ```

3. **Select correct microphone:**
   - Windows might have multiple audio devices
   - Set your preferred mic as default in Windows Sound settings

---

## LLM Response Issues

### "Not responding" or long delays

**For Groq mode:**
- Check internet connection
- Verify API key is valid
- Check [status.groq.com](https://status.groq.com) for service status

**For Gemini mode:**
- Verify API key
- Check Google API quotas
- Try switching to Groq mode

**For Ollama mode:**
- Make sure Ollama is running: `ollama serve`
- Check model is downloaded: `ollama list`
- Try: `ollama pull llama3.2`

### Responses in wrong language
- System should auto-detect language
- "hello" → English response
- "namaste" → Hindi response
- If wrong, restart Desktop Buddy with updated config

### "Fallback to Ollama" messages
**This is normal!** If primary API (Groq/Gemini) fails, Desktop Buddy automatically uses Ollama.

**To fix:**
1. Make sure Ollama is installed and running
2. Pull a model: `ollama pull llama3.2`
3. Check Ollama status: `ollama list`

---

## Voice/TTS Issues

### No voice output
**Check:**
1. Volume is not muted
2. Correct audio output device selected
3. Internet connection (Edge TTS requires internet)

### Voice sounds robotic or wrong accent
**Solution:** Change voice preset in `config.json`:
```json
{
  "tts": {
    "voice_preset": "indian_english"  // or "anime_english", "hinglish"
  }
}
```

### TTS interrupted but keeps speaking
**This is a known issue.** The interrupt detection should stop TTS when you start speaking. If it doesn't:
1. Restart Desktop Buddy
2. Speak clearly and loudly to trigger interrupt
3. Check microphone sensitivity

---

## Performance Issues

### Application slow to start
**Normal behavior:** First launch takes longer to initialize all components.

**If consistently slow:**
- Check antivirus isn't scanning the .exe
- Run from SSD instead of HDD
- Close other heavy applications

### High CPU usage
**Causes:**
- Ollama using CPU for inference (normal for local AI)
- Continuous microphone monitoring (normal)
- Multiple backends running

**Solutions:**
- Use Groq instead of Ollama (faster, uses cloud)
- Close when not in use
- Disable sentiment analysis in config if not needed

---

## Configuration Issues

### Lost my config.json
**Solution:** Copy from `config.template.json`:
```bash
copy config.template.json config.json
```
Then run Desktop Buddy - setup wizard will appear.

### Want to reset to defaults
**Solution:**
```bash
# Backup current config
copy config.json config.backup.json

# Delete config to trigger setup wizard
del config.json

# Restart Desktop Buddy
```

---

## Build Issues (For Developers)

### PyInstaller build fails
**Common causes:**
1. **Missing dependencies:**
   ```bash
   pip install pyinstaller
   pip install -r requirements.txt
   ```

2. **Hidden imports not found:**
   - Add to `DesktopBuddy.spec` in `hiddenimports` list

3. **Assets not bundled:**
   - Check `datas` section in `.spec` file
   - Make sure asset paths exist

### Executable crashes on startup
**Debug:**
1. Run with console window visible:
   - In `.spec` file, set `console=True`
2. Check error messages in console
3. Common issues:
   - Missing config.json (should trigger setup wizard)
   - Missing dependencies (rebuild with all dependencies)

---

## Getting Help

1. **Check README.md** for feature documentation
2. **Check INSTALL.md** for installation steps
3. **GitHub Issues:** Report bugs with:
   - Error message/screenshot
   - Steps to reproduce
   - Your config.json (remove API keys!)
   - Desktop Buddy version

---

**Still having issues?** Create a GitHub issue with detailed info!
