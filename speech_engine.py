"""
speech_engine.py - Robust Multi-Tier Speech-to-Text (STT) and Text-to-Speech (TTS) Engine.
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

# Windows SAPI5 TTS
HAS_WIN32COM = False
if os.name == 'nt':
    try:
        import win32com.client
        HAS_WIN32COM = True
    except ImportError:
        pass

# pyttsx3 TTS fallback
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

# Vosk offline STT
try:
    import vosk
    HAS_VOSK = True
except ImportError:
    HAS_VOSK = False


def clean_text_for_speech(raw_text: str) -> str:
    """Strips markdown, emojis and URLs so TTS speaks naturally."""
    if not raw_text:
        return ""
    text = re.sub(r'https?://\S+|www\.\S+', '', raw_text)
    text = re.sub(r'[\*\#\_\`\[\]\~\>]', '', text)
    text = re.sub(r'[^\w\s\.\,\!\?\-\'\":]', '', text)
    return text.strip()


class TextToSpeechEngine:
    """
    Multi-Tier TTS:
    1. Windows SAPI5 (win32com) — 100% offline, most reliable
    2. pyttsx3 — cross-platform offline fallback
    """
    def __init__(self):
        self.sapi_speaker = None
        self.pyttsx_engine = None

        if HAS_WIN32COM:
            try:
                self.sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                try:
                    voices = self.sapi_speaker.GetVoices()
                    target = config.VOICE_GENDER.lower()
                    for i in range(voices.Count):
                        desc = voices.Item(i).GetDescription().lower()
                        if target == "female" and any(k in desc for k in ("zira", "female", "hazel")):
                            self.sapi_speaker.Voice = voices.Item(i)
                            break
                        elif target == "male" and any(k in desc for k in ("david", "male", "george")):
                            self.sapi_speaker.Voice = voices.Item(i)
                            break
                except Exception:
                    pass
                print("[TTS]: Windows SAPI5 voice engine ready.")
            except Exception as e:
                print(f"[TTS Warning]: SAPI5 failed ({e}), trying pyttsx3...")
                self.sapi_speaker = None

        if not self.sapi_speaker and HAS_PYTTSX3:
            try:
                self.pyttsx_engine = pyttsx3.init()
                self.pyttsx_engine.setProperty('rate', config.VOICE_RATE)
                self.pyttsx_engine.setProperty('volume', config.VOICE_VOLUME)
                print("[TTS]: pyttsx3 voice engine ready.")
            except Exception as e:
                print(f"[TTS Warning]: pyttsx3 failed ({e})")
                self.pyttsx_engine = None

    def speak(self, text: str):
        """Speak text out loud and print to console."""
        if not text or not text.strip():
            return
        print(f"\n[{config.ASSISTANT_NAME}]: {text}")
        spoken = clean_text_for_speech(text) or text

        if self.sapi_speaker:
            try:
                self.sapi_speaker.Speak(spoken)
                return
            except Exception as e:
                print(f"[TTS Error]: {e}")

        if self.pyttsx_engine:
            try:
                self.pyttsx_engine.say(spoken)
                self.pyttsx_engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error]: {e}")


class SpeechToTextEngine:
    """
    STT engine with tuned sensitivity and smart online/offline fallback.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Low energy threshold = picks up quiet/normal speech easily
        self.recognizer.energy_threshold = config.ENERGY_THRESHOLD
        # Dynamic adjustment ON — adapts in real-time to your environment
        self.recognizer.dynamic_energy_threshold = True
        # Short pause = responds immediately after you stop talking
        self.recognizer.pause_threshold = config.PAUSE_THRESHOLD
        # How long it waits before deciding phrase ended
        self.recognizer.non_speaking_duration = 0.4

    def get_microphone_device(self) -> sr.Microphone:
        """Returns configured microphone device."""
        return sr.Microphone(device_index=config.MICROPHONE_INDEX)

    def calibrate_ambient_noise(self, microphone: sr.Microphone):
        """One-time ambient noise calibration at startup."""
        print("Calibrating microphone (1 second, please stay quiet)...")
        with microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            # Cap threshold so it doesn't become too aggressive
            if self.recognizer.energy_threshold > 400:
                self.recognizer.energy_threshold = 250
        print(f"[MIC READY]: Energy threshold set to {self.recognizer.energy_threshold:.0f}")

    def listen_and_recognize(self, microphone: sr.Microphone,
                             timeout: int = 5, phrase_time_limit: int = 10) -> str:
        """
        Listens once and returns recognized text.
        Returns empty string on timeout or unclear audio — caller loops back.
        """
        try:
            with microphone as source:
                print("[Listening...] Speak now")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            print("[Processing...]")

            # Try Google STT (online)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"[Heard]: \"{text}\"")
                return text.strip()
            except sr.RequestError:
                # Internet is offline — try Vosk
                print("[Offline] Trying Vosk offline recognition...")
                if HAS_VOSK:
                    try:
                        text = self.recognizer.recognize_vosk(audio)
                        if text:
                            print(f"[Heard (offline)]: \"{text}\"")
                            return text.strip()
                    except Exception:
                        pass
                return ""

        except sr.WaitTimeoutError:
            # No speech heard within timeout — this is normal, just loop back
            return ""
        except sr.UnknownValueError:
            print("[Could not understand] Try speaking more clearly or closer to the mic.")
            return ""
        except Exception as e:
            print(f"[STT Error]: {e}")
            return ""
