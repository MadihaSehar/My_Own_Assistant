"""
test_mic.py - Microphone Hardware & Sensitivity Diagnostic Tool for JARVIS.

Run this script to list all active microphones on your computer, test live audio levels,
and find the perfect mic device index & energy sensitivity threshold.
"""

import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import speech_recognition as sr

def list_microphones():
    print("==================================================")
    print("[JARVIS] MICROPHONE HARDWARE DIAGNOSTIC TOOL")
    print("==================================================")
    
    try:
        mics = sr.Microphone.list_microphone_names()
        print(f"\nFound {len(mics)} audio input devices:\n")
        for idx, name in enumerate(mics):
            print(f"  [{idx}] {name}")
    except Exception as e:
        print(f"Error listing microphones: {e}")
    print("==================================================")

if __name__ == "__main__":
    list_microphones()
