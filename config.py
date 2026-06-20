import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Export variables with specified defaults
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
CAPTURE_INTERVAL = float(os.getenv("CAPTURE_INTERVAL", 10.0))
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", 3.0))
OVERLAY_OPACITY = float(os.getenv("OVERLAY_OPACITY", 0.15))
OVERLAY_TEXT_SIZE = int(os.getenv("OVERLAY_TEXT_SIZE", 18))
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", 3))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 4000))
HOTKEY = os.getenv("HOTKEY", "<ctrl>+<shift>+p")
