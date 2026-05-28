import base64
import logging
import os
import sys
from io import BytesIO
import PIL.Image
import config

import numpy as np

def encode_image_to_base64(image: PIL.Image.Image) -> str:
    """
    Saves image to an in-memory BytesIO buffer as JPEG at IMAGE_JPEG_QUALITY,
    Base64-encodes the buffer, and returns the encoded string.
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=config.IMAGE_JPEG_QUALITY)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def has_screen_changed(img1: PIL.Image.Image, img2: PIL.Image.Image, threshold: float = 1.0) -> bool:
    """
    Compares two Pillow images using Mean Squared Error (MSE).
    Returns True if the MSE exceeds the threshold, implying a noticeable change.
    """
    if img1 is None or img2 is None:
        return True
    
    # Convert images to numpy arrays
    arr1 = np.array(img1).astype("float")
    arr2 = np.array(img2).astype("float")
    
    # Check if dimensions match
    if arr1.shape != arr2.shape:
        return True
        
    rmse = np.sqrt(np.mean((arr1 - arr2) ** 2))
    return rmse > threshold

def setup_logger(name: str) -> logging.Logger:
    """
    Writes logs to logs/app.log and stdout.
    Format: [TIMESTAMP] [LEVEL] message
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(os.path.join("logs", "app.log")),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    return logging.getLogger(name)
