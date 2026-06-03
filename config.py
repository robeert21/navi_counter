import os
import sys
from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    _base = sys._MEIPASS
else:
    _base = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(_base, ".env"))

YOUTUBE_VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID", "")
WS_PORT = int(os.getenv("WS_PORT", "8765"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
