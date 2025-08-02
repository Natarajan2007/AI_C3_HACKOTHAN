import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Llama API Configuration
    LLAMA_API_KEY = "b7bb07f8a38beab538acaa7bd0dd1ad7bc22e4c64ef0c98b386571d2f0a35db9"
    LLAMA_API_URL = "https://api.together.xyz/v1/chat/completions"
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = True
    
    # Negotiation Settings
    MAX_ROUNDS = 10
    TIMEOUT_SECONDS = 30
    
    # Voice Settings
    VOICE_ENABLED = True
    TTS_RATE = 150
    TTS_VOLUME = 0.9
