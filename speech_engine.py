"""
speech_engine.py - Speech-to-Text (STT) and Text-to-Speech (TTS) integration module.
"""

import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pyttsx3
import speech_recognition as sr
import config


class TextToSpeechEngine:
    """
    Wrapper around pyttsx3 for cross-platform offline Text-to-Speech synthesis.
    """
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self._configure_voice()
        except Exception as e:
            print(f"[TTS Warning] Failed to initialize pyttsx3: {e}. Console speech fallback enabled.")
            self.engine = None

    def _configure_voice(self):
        if not self.engine:
            return
        
        # Set speech rate and volume
        self.engine.setProperty('rate', config.VOICE_RATE)
        self.engine.setProperty('volume', config.VOICE_VOLUME)
        
        # Select target voice (Male / Female)
        try:
            voices = self.engine.getProperty('voices')
            target_gender = config.VOICE_GENDER.lower()
            
            for voice in voices:
                voice_name = voice.name.lower()
                if target_gender == "female" and ("female" in voice_name or "zira" in voice_name or "hazel" in voice_name):
                    self.engine.setProperty('voice', voice.id)
                    break
                elif target_gender == "male" and ("male" in voice_name or "david" in voice_name or "george" in voice_name):
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"[TTS Voice Config Warning] Could not configure voice property: {e}")

    def speak(self, text: str):
        """
        Prints and speaks the provided text response out loud.
        """
        print(f"\n[{config.ASSISTANT_NAME}]: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error] {e}")


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
        
        Args:
            microphone (sr.Microphone): PyAudio microphone instance.
            timeout (int): Seconds to wait for speech before timing out.
            phrase_time_limit (int): Max seconds allowed for a single spoken phrase.
        Returns:
            str: Recognized text string (lowercase), or empty string if unrecognised.
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
            # Listening timed out waiting for audio input (normal in continuous loop)
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
