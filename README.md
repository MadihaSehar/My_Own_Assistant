# 🤖 JARVIS - Modular AI Voice Assistant

A modular, hands-free personal voice assistant built in Python. Features Speech-to-Text (STT), OpenAI LLM Tool Calling (Function Calling), system tool execution, and Text-to-Speech (TTS) audio output.

---

## 📁 Architecture Overview

```text
voice_assistant/
│
├── config.py             # Global configuration, app shortcuts, and voice settings
├── tools.py              # System execution tools (Search, App Control, Utility, YouTube)
├── speech_engine.py      # STT (Microphone listening) & TTS (pyttsx3 speech output)
├── ai_brain.py           # LLM Function Calling engine & rule-based fallback
├── main.py               # Continuous event loop & ambient noise calibration
├── requirements.txt      # Python dependencies list
└── .env.example          # Environment variable template for API keys
```

---

## 🛠️ Implemented System Tools

1. **Web Search (`web_search`)**: Searches Google or opens web URLs directly in the default system browser.
2. **App Control (`open_application`)**: Launches Windows desktop apps (Notepad, Calculator, Chrome, Command Prompt, Paint, File Explorer, Task Manager).
3. **Utility Info (`get_utility_info`)**: Fetches system date, current time, or real-time weather via `wttr.in`.
4. **Media Playback (`play_media`)**: Searches and plays songs or videos on YouTube using `pywhatkit`.

---

## 🚀 Step-by-Step Setup Guide

### 1. Clone / Open Project Workspace
Navigate to the project folder in your terminal:
```bash
cd C:\Users\madih\.gemini\antigravity\scratch\voice_assistant
```

### 2. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

> **Note for Windows PyAudio Installation**:
> If `pip install pyaudio` fails due to missing C compilers, install PyAudio via wheel or `pipwin`:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 3. Configure Environment Variables (Optional)
Copy `.env.example` to `.env` and add your OpenAI API Key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

*Note: If no API key is provided, JARVIS automatically runs in **Rule-Based Local Fallback Mode**, so all local tool commands work out-of-the-box!*

### 4. Run the Assistant
Launch the main assistant event loop:
```bash
python main.py
```

---

## 🗣️ Example Voice Commands

- **Web Search**: *"Search Google for Python tutorials"* or *"Look up quantum computing"*
- **App Control**: *"Open Notepad"*, *"Launch Calculator"*, or *"Start Chrome"*
- **Utility Info**: *"What is the time?"*, *"What's today's date?"*, *"What is the weather in Tokyo?"*
- **Media**: *"Play Bohemian Rhapsody on YouTube"* or *"Play Lofi hip hop music"*
- **Exit**: *"Exit"*, *"Goodbye"*, *"Stop"*, or press `Ctrl+C`

---

## 🧩 How to Customize & Add New Commands

Adding a new tool to JARVIS takes just 3 quick steps in `tools.py`:

### Step 1: Write your Python Function
```python
def get_system_battery() -> str:
    """Returns battery status."""
    import psutil
    battery = psutil.sensors_battery()
    return f"Battery is at {battery.percent}%"
```

### Step 2: Add Function Schema to `TOOLS_SCHEMA`
```python
{
    "type": "function",
    "function": {
        "name": "get_system_battery",
        "description": "Gets current laptop battery percentage.",
        "parameters": {"type": "object", "properties": {}}
    }
}
```

### Step 3: Register in `TOOL_DISPATCHER`
```python
TOOL_DISPATCHER = {
    ...
    "get_system_battery": get_system_battery
}
```
That's it! OpenAI will automatically recognize when the user asks for battery info and execute your function.
