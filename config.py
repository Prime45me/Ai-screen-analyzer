import os
from dotenv import load_dotenv

# Load all values from a .env file using python-dotenv
load_dotenv()

# Export configuration variables with specified defaults
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", 15))
OVERLAY_OPACITY = float(os.getenv("OVERLAY_OPACITY", 0.6)) # Increased for readability
OVERLAY_TEXT_SIZE = int(os.getenv("OVERLAY_TEXT_SIZE", 22))
OVERLAY_HEADER_SIZE = int(os.getenv("OVERLAY_HEADER_SIZE", 28))
IMAGE_RESIZE_FACTOR = float(os.getenv("IMAGE_RESIZE_FACTOR", 0.5))
IMAGE_JPEG_QUALITY = int(os.getenv("IMAGE_JPEG_QUALITY", 70))
HOTKEY = os.getenv("HOTKEY", "<ctrl>+<shift>+space")
AUTO_PAUSE_SECONDS = int(os.getenv("AUTO_PAUSE_SECONDS", 30))
