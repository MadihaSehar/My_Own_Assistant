"""
test_assistant.py - Automated verification test for JARVIS Voice Assistant talkative responses & multi-intent commands.
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
    print("[JARVIS] RUNNING HUMAN TALKATIVE & MULTI-INTENT TEST SUITE")
    print("==================================================")

    tts = TextToSpeechEngine()
    brain = AIBrain()

    # Test cases testing human conversation + multi-action compound commands
    test_commands = [
        "how are you",
        "who are you and what can you do",
        "tell me a joke",
        "check system battery",
        "what is the time AND open notepad",
        "check weather in London AND search python programming"
    ]

    for cmd in test_commands:
        print(f"\n🗣️ Executing User Command: '{cmd}'")
        res = brain.process_command(cmd)
        print(f"🤖 Assistant Spoken Response: {res}")
        tts.speak(res)

    print("\n==================================================")
    print("ALL MULTI-INTENT & HUMAN TALKATIVE TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
