import os
from dotenv import load_dotenv

load_dotenv()

try:
    from _secrets import YOUTUBE_API_KEY, GEMINI_API_KEY
except ImportError:
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID", "")
WS_PORT = int(os.getenv("WS_PORT", "8765"))
