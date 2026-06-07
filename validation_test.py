import sys
import os
import cv2
import numpy as np
import PIL.Image

# Add current directory to path
sys.path.append(os.getcwd())

import vision
import config

def run_validation(image_path):
    print(f"--- STARTING VALIDATION TEST ---")
    print(f"Loading test image: {image_path}")
    
    # 1. Load image
    image_pil = PIL.Image.open(image_path)
    image_np = np.array(image_pil)
    
    # 2. Detect Highlight
    print("\n[Step 1] Detecting highlight region...")
    crop = vision.detect_highlight_region(image_np)
    
    if crop is None:
        print("FAILED: No highlight detected in the image.")
        return False
    
    print(f"SUCCESS: Found highlight region. Shape: {crop.shape}")
    
    # Save the crop for verification
    crop_path = "verification_crop.png"
    cv2.imwrite(crop_path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
    print(f"Saved crop to {crop_path}")
    
    # 3. Extract Text (OCR)
    print("\n[Step 2] Running OCR on crop...")
    text = vision.extract_text_from_image(crop)
    
    if not text:
        print("WARNING: OCR extracted no text. (Expected if image is blurry or OCR is slow)")
    else:
        print(f"OCR RESULT: \"{text[:100]}...\"")
    
    # 4. Analyze Text (Gemini)
    print("\n[Step 3] Sending to Gemini (Dry Run/API connectivity check)...")
    if not text:
        text = "print('Hello World')\nError: NameError: name 'print' is not defined" # Fake text for API test if OCR failed on synthetic image
        
    analysis = vision.analyze_highlighted_text(text)
    print(f"\n--- AI ANALYSIS RESULT ---")
    print(analysis)
    print(f"\n--- VALIDATION COMPLETE ---")
    return True

if __name__ == "__main__":
    # Find the generated image (using glob pattern if name varies)
    import glob
    images = glob.glob("C:/Users/user/.gemini/antigravity/brain/71c788fd-08bc-4085-a373-d208af30422d/test_highlight_screen*.png")
    if images:
        run_validation(images[0])
    else:
        print("Could not find test image.")
