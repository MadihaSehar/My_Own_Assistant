"""
main.py - Main entry point and continuous event loop for JARVIS Personal Voice Assistant.
"""

import sys
import io
import time

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


def print_banner(mic_info: str):
    """Prints status banner to terminal."""
    banner = f"""
    ============================================================
       [JARVIS] - Personal AI Voice Assistant
    ============================================================
       Status    : Active & Ready
       Provider  : {config.LLM_PROVIDER.upper()} Mode
       Audio Mic : {mic_info}
       Threshold : {config.ENERGY_THRESHOLD}
       Commands  : "how are you", "open notepad",
                   "what time is it", "weather in [city]",
                   "play [song] on youtube", "exit" to quit
    ============================================================
    """
    print(banner)


def main():
    """Main execution loop - pure continuous microphone listening."""

    # ── Step 1: Boot subsystems ──────────────────────────────
    tts = TextToSpeechEngine()
    stt = SpeechToTextEngine()
    brain = AIBrain()

    # ── Step 2: Connect microphone ──────────────────────────
    mic_index = config.MICROPHONE_INDEX
    mic_label = f"Device [{mic_index}]" if mic_index is not None else "Default Microphone"
    print_banner(mic_label)

    try:
        microphone = stt.get_microphone_device()
        stt.calibrate_ambient_noise(microphone)
        tts.speak(f"Hello! I am {config.ASSISTANT_NAME}, your personal voice assistant. How can I help you?")
        mic_ok = True
    except Exception as e:
        print(f"\n[Microphone Error]: {e}")
        print("[Fallback]: Keyboard mode active. Type commands below.\n")
        microphone = None
        mic_ok = False
        tts.speak(f"Microphone not found. Running in keyboard mode. Type your commands.")

    # ── Step 3: Continuous loop ─────────────────────────────
    print("\n[READY]: JARVIS is listening. Speak now...\n")
    
    while True:
        command_text = ""

        try:
            if mic_ok and microphone:
                # ── Pure microphone mode ──────────────────────
                command_text = stt.listen_and_recognize(microphone, timeout=5, phrase_time_limit=10)

            else:
                # ── Keyboard fallback (only when mic unavailable) ──
                try:
                    command_text = input("Type command: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

        except KeyboardInterrupt:
            print("\n[JARVIS]: Keyboard interrupt received.")
            tts.speak("Shutting down. Goodbye!")
            break
        except Exception as e:
            print(f"[Listen Error]: {e}")
            time.sleep(0.5)
            continue

        # ── Skip empty results and keep looping immediately ──
        if not command_text or not command_text.strip():
            continue

        print(f"\n>>> Heard: \"{command_text}\"")

        # ── Check for exit commands ───────────────────────────
        cleaned = command_text.lower().strip()
        if any(cleaned == cmd or cleaned.startswith(cmd) for cmd in EXIT_COMMANDS):
            tts.speak(f"Goodbye! Shutting down {config.ASSISTANT_NAME}.")
            print("\n[JARVIS]: Shut down cleanly.")
            break

        # ── Process intent → Execute tools → Speak response ──
        try:
            response = brain.process_command(command_text)
            if response:
                tts.speak(response)
        except Exception as e:
            print(f"[Brain Error]: {e}")
            tts.speak("Sorry, I ran into an error. Please try again.")

        print("\n[READY]: Listening again...\n")


if __name__ == "__main__":
    main()
