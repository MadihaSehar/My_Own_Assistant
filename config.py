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
ASSISTANT_NAME = "JARVIS"
VOICE_GENDER = "female"  # 'male' or 'female'
VOICE_RATE = 175         # Words per minute (default ~200, 175 is clear)
VOICE_VOLUME = 1.0       # Volume (0.0 to 1.0)

# --- Audio STT Settings ---
ENERGY_THRESHOLD = 300   # Speech recognition sensitivity threshold
CALIBRATION_DURATION = 1  # Seconds to calibrate for ambient noise

# --- LLM Provider Settings ---
# Supported providers: "openai" or "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# --- Application Launcher Mapping (Windows / Cross-platform shortcuts) ---
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
    "task manager": "taskmgr.exe"
}
