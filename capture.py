import mss
import numpy as np
import cv2
import PIL.Image
import config

def capture_screen() -> PIL.Image.Image:
    """
    Captures the primary monitor screenshot using MSS.
    Converts raw pixel data to a NumPy array (BGR),
    resizes by IMAGE_RESIZE_FACTOR using cv2.INTER_AREA,
    and returns a Pillow Image in RGB mode.
    Does NOT save to disk.
    """
    with mss.mss() as sct:
        # 1. Grab the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # 2. Convert raw pixel data to a NumPy array
        # mss.grab returns an SCTImage which can be converted to a NumPy array (BGRA)
        img_np = np.array(sct_img)
        
        # 3. Convert BGRA to BGR for OpenCV processing
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        
        # 4. Resize if factor is not 1.0
        if config.IMAGE_RESIZE_FACTOR != 1.0:
            new_width = int(img_bgr.shape[1] * config.IMAGE_RESIZE_FACTOR)
            new_height = int(img_bgr.shape[0] * config.IMAGE_RESIZE_FACTOR)
            img_bgr = cv2.resize(img_bgr, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # 5. Convert back to RGB for Pillow
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # 6. Convert to Pillow Image object
        img_pil = PIL.Image.fromarray(img_rgb)
        
        return img_pil
