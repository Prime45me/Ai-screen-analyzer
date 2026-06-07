import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Export variables with specified defaults
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", 0.3))
OVERLAY_OPACITY = float(os.getenv("OVERLAY_OPACITY", 0.15))
OVERLAY_TEXT_SIZE = int(os.getenv("OVERLAY_TEXT_SIZE", 18))
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", 3))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 4000))
HOTKEY = os.getenv("HOTKEY", "<ctrl>+<shift>+p")
