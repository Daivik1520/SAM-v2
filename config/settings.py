"""
Enhanced SAM AI Assistant - Configuration Settings
"""
import os
from pathlib import Path

# Base Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True)

# UI Configuration
UI_CONFIG = {
    "theme": "dark",
    "appearance_mode": "dark",
    "color_theme": "blue",
    "window_size": (1200, 800),
    "min_window_size": (800, 600),
    "transparency": 0.95,
    "animation_speed": 0.3,
    "font_family": "Segoe UI",
    "font_size": 12
}

# Voice Configuration
VOICE_CONFIG = {
    "recognition_timeout": 5,
    "phrase_timeout": 1,
    "energy_threshold": 4000,
    "dynamic_energy_threshold": True,
    "tts_rate": 200,
    "tts_volume": 0.8,
    "wake_word": "sam",
    "language": "en-US",
    "voice_id": 0
}

# AI Configuration
AI_CONFIG = {
    "model_name": "gpt-3.5-turbo",
    "max_tokens": 2000,
    "temperature": 0.7,
    "context_window": 10,
    "enable_rag": True,
    "enable_memory": True,
    "personality": "helpful_assistant"
}

# Computer Vision Configuration
CV_CONFIG = {
    "camera_index": 0,
    "face_detection_model": "haarcascade_frontalface_default.xml",
    "object_detection_confidence": 0.5,
    "gesture_recognition": True,
    "emotion_detection": True,
    "ocr_language": "eng"
}

# System Configuration
SYSTEM_CONFIG = {
    "monitoring_interval": 1,
    "max_cpu_usage": 80,
    "max_memory_usage": 80,
    "auto_cleanup": True,
    "backup_interval": 24,  # hours
    "log_level": "INFO"
}

# Security Configuration
SECURITY_CONFIG = {
    "encryption_key": None,  # Will be generated
    "biometric_auth": False,
    "privacy_mode": False,
    "secure_storage": True,
    "session_timeout": 30  # minutes
}

# API Keys (to be set via environment variables)
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "google_search": os.getenv("GOOGLE_SEARCH_API_KEY"),
    "weather": os.getenv("WEATHER_API_KEY"),
    "news": os.getenv("NEWS_API_KEY"),
    "spotify": os.getenv("SPOTIFY_API_KEY"),
    "calendar": os.getenv("CALENDAR_API_KEY")
}

# Feature Flags
FEATURES = {
    "voice_control": True,
    "computer_vision": True,
    "smart_home": True,
    "productivity": True,
    "entertainment": True,
    "health_wellness": True,
    "security": True,
    "learning": True,
    "gaming": True,
    "web_integration": True
}