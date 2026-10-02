"""
config.py - Global configuration and environment settings for JARVIS Voice Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# --- Assistant Settings ---
ASSISTANT_NAME = "Madhu"
VOICE_GENDER = "female"  # 'male' or 'female'
VOICE_RATE = 175         # Words per minute (175 is clear & natural)
VOICE_VOLUME = 1.0       # Volume (0.0 to 1.0)
CONVERSATION_HISTORY_LIMIT = 10  # Remember last N conversation turns

# --- Audio STT & Microphone Settings ---
# Set MICROPHONE_INDEX to None for default mic, or integer (e.g. 1, 6, 13) for specific device
MICROPHONE_INDEX = int(os.getenv("MICROPHONE_INDEX", "-1"))
if MICROPHONE_INDEX == -1:
    MICROPHONE_INDEX = None

ENERGY_THRESHOLD = 150   # Sensitive energy threshold (lower = more sensitive to soft voice)
PAUSE_THRESHOLD = 0.8    # Seconds of non-speaking audio before phrase is considered complete
CALIBRATION_DURATION = 1  # Seconds to calibrate for ambient noise

# --- LLM Provider Settings ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# --- Application Launcher Mapping ---
APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "browser": "chrome.exe",
    "chrome": "chrome.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "spotify": "spotify.exe",
    "edge": "msedge.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe"
}
