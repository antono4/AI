"""
AI Video Shorts App - Configuration
Configure semua API keys dan settings di sini
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============== API KEYS ==============
# OpenAI (GPT untuk content generation, TTS)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Anthropic (Claude untuk advanced content)
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# ElevenLabs (Premium AI Voice)
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')

# Replicate (AI Video Generation - Runway, Pika, etc.)
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN', '')

# Pexels (Stock Video)
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', '')

# Pixabay (Stock Video)
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY', '')

# YouTube API
YOUTUBE_CLIENT_SECRET = os.getenv('YOUTUBE_CLIENT_SECRET', 'client_secret.json')
YOUTUBE_TOKEN_PICKLE = os.getenv('YOUTUBE_TOKEN_PICKLE', 'youtube_token.pickle')

# ============== VIDEO SETTINGS ==============
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # Vertical (9:16)
VIDEO_FPS = 30
VIDEO_DURATION_MIN = 30  # seconds
VIDEO_DURATION_MAX = 60  # seconds

# ============== CONTENT SETTINGS ==============
DEFAULT_LANGUAGE = 'id'  # Indonesia
DEFAULT_VOICE = 'id-ID'  # Indonesian voice
BACKGROUND_MUSIC_VOLUME = 0.3
VOICE_VOLUME = 1.0

# ============== OUTPUT PATHS ==============
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
VIDEOS_DIR = os.getenv('VIDEOS_DIR', 'videos')
TEMP_DIR = os.getenv('TEMP_DIR', 'temp')
LOGS_DIR = os.getenv('LOGS_DIR', 'logs')

# ============== YOUTUBE SETTINGS ==============
DEFAULT_VIDEO_CATEGORY = '22'  # People & Blogs
DEFAULT_PRIVACY_STATUS = 'private'  # private, public, unlisted
AUTO_GENERATE_THUMBNAIL = True

# ============== SCHEDULER SETTINGS ==============
ENABLE_AUTO_SCHEDULE = os.getenv('ENABLE_AUTO_SCHEDULE', 'true').lower() == 'true'
DEFAULT_SCHEDULE_TIME = '09:00'  # 9 AM
SCHEDULE_TIMEZONE = 'Asia/Jakarta'

# ============== AI MODELS ==============
CONTENT_MODEL = os.getenv('CONTENT_MODEL', 'gpt-4-turbo-preview')
IMAGE_MODEL = os.getenv('IMAGE_MODEL', 'dall-e-3')
VIDEO_MODEL = os.getenv('VIDEO_MODEL', 'runway Gen-2')

# ============== RATE LIMITS ==============
MAX_DAILY_VIDEOS = int(os.getenv('MAX_DAILY_VIDEOS', '10'))
MAX_CONCURRENT_UPLOADS = int(os.getenv('MAX_CONCURRENT_UPLOADS', '2'))