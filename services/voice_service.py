import pyttsx3
import speech_recognition as sr
import threading
from typing import Optional
from config import Config

class VoiceService:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure TTS
        self.tts_engine.setProperty('rate', Config.TTS_RATE)
        self.tts_engine.setProperty('volume', Config.TTS_VOLUME)
        
        # Set voice (try different voices)
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Use female voice for seller, male for buyer
            self.seller_voice = voices[1] if len(voices) > 1 else voices[0]
            self.buyer_voice = voices[0] if len(voices) > 0 else None
    
    def text_to_speech(self, text: str, agent_role: str = "buyer"):
        """Convert text to speech"""
        if not Config.VOICE_ENABLED:
            return
            
        try:
            # Set voice based on agent role
            if agent_role == "seller" and hasattr(self, 'seller_voice'):
                self.tts_engine.setProperty('voice', self.seller_voice.id)
            elif agent_role == "buyer" and hasattr(self, 'buyer_voice'):
                self.tts_engine.setProperty('voice', self.buyer_voice.id)
            
            # Speak in a separate thread to avoid blocking
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def speech_to_text(self, timeout: int = 5) -> Optional[str]:
        """Convert speech to text"""
        try:
            with self.microphone as source:
                print("Listening...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            print("Speech recognition timeout")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def set_voice_for_agent(self, agent_role: str):
        """Set voice based on agent role"""
        voices = self.tts_engine.getProperty('voices')
        if not voices:
            return
            
        if agent_role == "seller" and len(voices) > 1:
            self.tts_engine.setProperty('voice', voices[1].id)  # Female voice
        elif agent_role == "buyer":
            self.tts_engine.setProperty('voice', voices[0].id)  # Male voice
