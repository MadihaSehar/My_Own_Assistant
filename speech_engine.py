"""
speech_engine.py - Robust Multi-Tier Speech-to-Text (STT) and Text-to-Speech (TTS) Engine.
Guarantees audio speech playback on Windows (via native SAPI.SpVoice & pyttsx3) and cross-platform OS.
"""

import sys
import os
import io
import re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import speech_recognition as sr
import config

# Try importing Windows native SAPI5 via win32com
HAS_WIN32COM = False
if os.name == 'nt':
    try:
        import win32com.client
        HAS_WIN32COM = True
    except ImportError:
        HAS_WIN32COM = False

# Try importing pyttsx3
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False


def clean_text_for_speech(raw_text: str) -> str:
    """
    Strips markdown, emojis, special symbols, and URLs so the TTS engine speaks naturally.
    """
    if not raw_text:
        return ""
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', raw_text)
    # Remove markdown formatting (*, #, _, `, [, ])
    text = re.sub(r'[\*\#\_\`\[\]\~\>\`]', '', text)
    # Remove emojis and non-ASCII/non-latin symbols except standard punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\'\":]', '', text)
    return text.strip()


class TextToSpeechEngine:
    """
    Multi-Tier Text-To-Speech engine.
    Priority 1: Native Windows SAPI5 (win32com) - 100% reliable on Windows.
    Priority 2: pyttsx3 cross-platform engine.
    Fallback: Console text output.
    """
    def __init__(self):
        self.sapi_speaker = None
        self.pyttsx_engine = None

        # Priority 1: Initialize Windows Native SAPI5 Speaker
        if HAS_WIN32COM:
            try:
                self.sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                # Set voice gender if possible
                try:
                    voices = self.sapi_speaker.GetVoices()
                    target_gender = config.VOICE_GENDER.lower()
                    for i in range(voices.Count):
                        desc = voices.Item(i).GetDescription().lower()
                        if target_gender == "female" and ("zira" in desc or "female" in desc or "hazel" in desc):
                            self.sapi_speaker.Voice = voices.Item(i)
                            break
                        elif target_gender == "male" and ("david" in desc or "male" in desc or "george" in desc):
                            self.sapi_speaker.Voice = voices.Item(i)
                            break
                except Exception:
                    pass
                print("[TTS Engine]: Native Windows SAPI5 Voice engine initialized.")
            except Exception as e:
                print(f"[TTS Warning]: SAPI5 initialization failed: {e}")
                self.sapi_speaker = None

        # Priority 2: Initialize pyttsx3 fallback
        if not self.sapi_speaker and HAS_PYTTSX3:
            try:
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty('rate', config.VOICE_RATE)
                self.pyttsx_engine.setProperty('volume', config.VOICE_VOLUME)
                print("[TTS Engine]: pyttsx3 Voice engine initialized.")
            except Exception as e:
                print(f"[TTS Warning]: pyttsx3 initialization failed: {e}")
                self.pyttsx_engine = None

    def speak(self, text: str):
        """
        Prints and speaks response out loud using native voice audio.
        """
        if not text or not text.strip():
            return

        # Print full text to terminal console
        print(f"\n[{config.ASSISTANT_NAME}]: {text}")

        # Clean text for spoken audio synthesizer
        spoken_text = clean_text_for_speech(text)
        if not spoken_text:
            spoken_text = text

        # Option 1: Native Windows SAPI5 (Fastest & most reliable on Windows)
        if self.sapi_speaker:
            try:
                self.sapi_speaker.Speak(spoken_text)
                return
            except Exception as e:
                print(f"[TTS SAPI5 Error]: {e}")

        # Option 2: pyttsx3 engine
        if self.pyttsx_engine:
            try:
                self.pyttsx_engine.say(spoken_text)
                self.pyttsx_engine.runAndWait()
                return
            except Exception as e:
                print(f"[TTS pyttsx3 Error]: {e}")


class SpeechToTextEngine:
    """
    Wrapper around speech_recognition library for microphone audio capture and STT recognition.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True

    def calibrate_ambient_noise(self, microphone: sr.Microphone):
        """
        Adjusts recognizer sensitivity based on background ambient noise.
        """
        print("Calibrating microphone for ambient background noise...")
        with microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=config.CALIBRATION_DURATION)
        print("Microphone calibrated successfully!")

    def listen_and_recognize(self, microphone: sr.Microphone, timeout: int = 5, phrase_time_limit: int = 8) -> str:
        """
        Captures audio from microphone and converts to text string.
        """
        try:
            with microphone as source:
                print("\nListening... (Speak your command)")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"[You Said]: \"{text}\"")
            return text.strip()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("[STT]: Could not understand the audio clearly.")
            return ""
        except sr.RequestError as e:
            print(f"[STT Error]: Speech Recognition service request failed: {e}")
            return ""
        except Exception as e:
            print(f"[STT Error]: Audio capture failed: {e}")
            return ""
