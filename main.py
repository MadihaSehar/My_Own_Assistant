"""
main.py - Main entry point and continuous event loop for JARVIS Personal Voice Assistant.
"""

import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import speech_recognition as sr
import config
from speech_engine import TextToSpeechEngine, SpeechToTextEngine
from ai_brain import AIBrain

EXIT_COMMANDS = {"exit", "quit", "stop", "goodbye", "bye", "shutdown", "turn off", "terminate"}


def print_banner():
    """Prints status banner to terminal."""
    mic_info = f"Device Index {config.MICROPHONE_INDEX}" if config.MICROPHONE_INDEX is not None else "Default Mic"
    banner = f"""
    ============================================================
       [JARVIS] - Personal AI Voice Assistant
    ============================================================
       Status    : Active & Ready
       Provider  : {config.LLM_PROVIDER.UPPER()} (Tool Calling Enabled)
       Audio Mic : {mic_info} (Sensitivity: {config.ENERGY_THRESHOLD})
       Commands  : "how are you", "open notepad", "play [song] on youtube", 
                   "what is the time", "weather in [city]", 
                   "search [query]", "exit" to quit.
    ============================================================
    """
    print(banner)


def main():
    """Main execution loop for continuous interaction."""
    print_banner()

    # Step 1: Initialize Assistant Subsystems
    tts = TextToSpeechEngine()
    stt = SpeechToTextEngine()
    brain = AIBrain()

    # Initial Greeting
    tts.speak(f"Hello! I am {config.ASSISTANT_NAME}, your personal voice assistant. How can I help you today?")

    # Step 2: Access Microphone for Audio Input
    try:
        microphone = stt.get_microphone_device()
        stt.calibrate_ambient_noise(microphone)
    except Exception as e:
        print(f"\n[Microphone Notice]: Could not initialize hardware mic ({e}).")
        print("Switching to Keyboard Text Mode for interaction...")
        microphone = None

    # Step 3: Continuous Interaction Loop
    while True:
        try:
            command_text = ""
            
            # Attempt microphone capture if microphone is available
            if microphone:
                command_text = stt.listen_and_recognize(microphone, timeout=5, phrase_time_limit=8)

            # If no spoken audio was detected or microphone timed out, offer instant text input fallback
            if not command_text:
                try:
                    command_text = input("⌨️ [Type command or press Enter to listen again]: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

            if not command_text:
                continue

            cleaned_text = command_text.lower().strip()
            if any(cleaned_text == cmd or cleaned_text.startswith(cmd) for cmd in EXIT_COMMANDS):
                tts.speak(f"Goodbye! Shutting down {config.ASSISTANT_NAME}.")
                print("\nAssistant shut down successfully.")
                break

            # Step 4: Process Intent & Execute Tools
            response_text = brain.process_command(command_text)

            # Step 5: Speak Output Response
            if response_text:
                tts.speak(response_text)

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected.")
            tts.speak("Shutting down voice assistant. Have a great day!")
            break
        except Exception as e:
            print(f"\nUnexpected Error: {e}")
            continue


if __name__ == "__main__":
    main()
