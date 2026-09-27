"""
main.py - Main entry point and continuous event loop for JARVIS Personal Voice Assistant.

Runs continuous voice listening, intents processing via LLM Tool Calling,
system execution of local tools, and Text-to-Speech audio response output.
"""

import sys
import io

# Force UTF-8 stdout encoding for Windows console compatibility
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import speech_recognition as sr
import config
from speech_engine import TextToSpeechEngine, SpeechToTextEngine
from ai_brain import AIBrain

# Termination commands that gracefully stop the voice assistant loop
EXIT_COMMANDS = {"exit", "quit", "stop", "goodbye", "bye", "shutdown", "turn off", "terminate"}


def print_banner():
    """Prints ASCII banner and active status to terminal."""
    banner = f"""
    ============================================================
       [JARVIS] - Personal AI Voice Assistant
    ============================================================
       Status   : Active & Ready
       Provider : {config.LLM_PROVIDER.upper()} (Tool Calling Enabled)
       Commands : "open notepad", "play [song] on youtube", 
                  "what is the time", "weather in [city]", 
                  "search [query]", "exit" to quit.
    ============================================================
    """
    print(banner)


def main():
    """Main execution loop for continuous hands-free interaction."""
    print_banner()

    # Step 1: Initialize Assistant Subsystems
    tts = TextToSpeechEngine()
    stt = SpeechToTextEngine()
    brain = AIBrain()

    # Initial Greeting
    tts.speak(f"Hello! I am {config.ASSISTANT_NAME}, your personal voice assistant. How can I help you today?")

    # Step 2: Access Microphone for Audio Input
    try:
        microphone = sr.Microphone()
        stt.calibrate_ambient_noise(microphone)
    except Exception as e:
        print(f"\n[Microphone Notice]: Could not initialize hardware mic ({e}).")
        print("Switching to Keyboard Text Fallback Mode for interaction...")
        microphone = None

    # Step 3: Continuous Hands-free Loop
    while True:
        try:
            # Capture input from microphone (or fallback keyboard input if no mic)
            if microphone:
                command_text = stt.listen_and_recognize(microphone, timeout=6, phrase_time_limit=10)
            else:
                command_text = input("\nType your command (or 'exit' to quit): ").strip()

            # Skip empty recognition results
            if not command_text:
                continue

            # Check for termination command
            cleaned_text = command_text.lower().strip()
            if any(cleaned_text == cmd or cleaned_text.startswith(cmd) for cmd in EXIT_COMMANDS):
                tts.speak(f"Goodbye! Shutting down {config.ASSISTANT_NAME}.")
                print("\nAssistant shut down successfully.")
                break

            # Step 4: Process Intent & Execute Tools via AI Brain
            response_text = brain.process_command(command_text)

            # Step 5: Speak Output Response
            if response_text:
                tts.speak(response_text)

        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected.")
            tts.speak("Shutting down voice assistant. Have a great day!")
            break
        except Exception as e:
            print(f"\nUnexpected Error in main loop: {e}")
            continue


if __name__ == "__main__":
    main()
