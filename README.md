# 🤖 JARVIS — Next-Gen Autonomous AI Voice Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/OpenAI-Function--Calling-green?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Function Calling">
  <img src="https://img.shields.io/badge/STT-SpeechRecognition-orange?style=for-the-badge" alt="SpeechRecognition">
  <img src="https://img.shields.io/badge/TTS-Windows%20SAPI5%20%2F%20pyttsx3-purple?style=for-the-badge" alt="TTS Engine">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="MIT License">
</p>

> **JARVIS** is a modular, production-grade, hands-free personal AI voice assistant built in Python. Powered by **OpenAI LLM Tool Calling (Function Calling)**, JARVIS converts natural spoken voice input into real-time operating system actions, web searches, media playback, hardware monitoring, news reports, and Wikipedia lookups.

---

## ✨ Key Features

- 🎙️ **Hands-Free Speech Recognition**: Continuous listening with automatic background ambient noise calibration using `speech_recognition`.
- 🧠 **LLM Tool Calling Integration**: Driven by OpenAI `gpt-4o-mini` function calling. JARVIS intelligently maps intent to Python functions.
- ⚡ **Rule-Based Local Fallback & Small Talk**: Works out-of-the-box even without an OpenAI API key! Uses an enhanced regex pattern engine for human conversational responses.
- 🔊 **Native Windows SAPI5 Text-to-Speech (TTS)**: 100% reliable voice speech synthesis out loud using built-in Windows voice drivers and `pyttsx3`.
- 🔀 **Multi-Action Compound Commands**: Execute multiple actions in a single spoken request (e.g., *"What is the time AND open Notepad AND check weather"*).
- 💻 **System & Desktop Control**: Launch applications like Notepad, Calculator, Chrome, Command Prompt, Task Manager, Paint, Word, Excel, Edge, and Spotify.
- 📸 **Screen Capture**: Take instant screenshots saved directly to your Pictures directory.
- 📊 **Hardware & Battery Monitoring**: Live CPU usage %, RAM memory consumption, and battery status.
- 📰 **Breaking News & Wikipedia Summaries**: Real-time BBC news headlines and concise Wikipedia knowledge lookup.
- 🔊 **Audio Volume Control**: Mute, unmute, increase, or decrease system audio volume via voice commands.

---

## ⚙️ Operating System Tools Matrix

| Tool | Function Name | Supported Spoken Intents / Commands |
| :--- | :--- | :--- |
| **App Launcher** | `open_application` | *"Open Notepad"*, *"Launch Calculator"*, *"Start Chrome"*, *"Open Spotify"* |
| **Web Search** | `web_search` | *"Search Google for Python tutorials"*, *"Look up quantum computing"* |
| **Media Player** | `play_media` | *"Play Bohemian Rhapsody on YouTube"*, *"Play Lofi hip hop music"* |
| **Wikipedia Knowledge** | `search_wikipedia` | *"Who is Albert Einstein"*, *"Search Wikipedia for artificial intelligence"* |
| **Screen Capture** | `take_screenshot` | *"Take a screenshot"*, *"Capture screen"* |
| **Hardware Monitor** | `get_system_resources` | *"Check CPU usage"*, *"Check RAM memory"*, *"Check system battery"* |
| **News Headlines** | `get_news_headlines` | *"Read top news"*, *"What are latest news headlines"* |
| **Volume Control** | `control_system_volume` | *"Mute audio"*, *"Unmute"*, *"Volume up"*, *"Volume down"* |
| **Utility Info** | `get_utility_info` | *"What's the time?"*, *"What day is it?"*, *"What is the weather in Tokyo?"* |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/MadihaSehar/My_Own_Assistant.git
cd My_Own_Assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch JARVIS
```bash
python main.py
```

---

## 🧪 Verification & Testing

To run the automated test suite and verify system execution:
```bash
python test_assistant.py
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
