"""
test_assistant.py - Automated verification test for JARVIS Voice Assistant tools and AI brain.
"""

import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from ai_brain import AIBrain
from speech_engine import TextToSpeechEngine
import tools

def run_tests():
    print("==================================================")
    print("[JARVIS] RUNNING AUTOMATED SUITE VERIFICATION")
    print("==================================================")

    # 1. Initialize Subsystems
    tts = TextToSpeechEngine()
    brain = AIBrain()

    # 2. Test Utility Tools
    print("\n--- Testing Utility Tool (Time & Date & Weather) ---")
    time_res = tools.get_utility_info("time")
    date_res = tools.get_utility_info("date")
    weather_res = tools.get_utility_info("weather", "New York")
    
    print(f"Time Output: {time_res}")
    print(f"Date Output: {date_res}")
    print(f"Weather Output: {weather_res}")
    
    tts.speak(time_res)
    tts.speak(weather_res)

    # 3. Test AI Brain Command Processing (Local Fallback / LLM Engine)
    print("\n--- Testing Intent Processing & Tool Execution ---")
    test_commands = [
        "what is the time",
        "weather in London",
        "open notepad",
        "search python programming",
        "play lofi beats on youtube"
    ]

    for cmd in test_commands:
        print(f"\nExecuting Test Command: '{cmd}'")
        res = brain.process_command(cmd)
        print(f"Assistant Spoken Response: {res}")
        tts.speak(res)

    print("\n==================================================")
    print("ALL SUITE TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
