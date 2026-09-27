"""
test_assistant.py - Automated verification test for JARVIS Voice Assistant features.
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

def run_tests():
    print("==================================================")
    print("[JARVIS] RUNNING EXTENDED FEATURE SUITE VERIFICATION")
    print("==================================================")

    tts = TextToSpeechEngine()
    brain = AIBrain()

    test_commands = [
        "how are you",
        "who is Albert Einstein",
        "check system resources",
        "read top news",
        "take a screenshot",
        "what is the time AND open calculator"
    ]

    for cmd in test_commands:
        print(f"\n🗣️ Executing User Command: '{cmd}'")
        res = brain.process_command(cmd)
        print(f"🤖 Assistant Spoken Response: {res}")
        tts.speak(res)

    print("\n==================================================")
    print("ALL EXTENDED SUITE FEATURE TESTS COMPLETED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
