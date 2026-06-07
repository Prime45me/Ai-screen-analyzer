import cv2
import numpy as np
import PIL.Image

def analyze_blue_range(image_path):
    image_pil = PIL.Image.open(image_path)
    image_np = np.array(image_pil)
    hsv = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)
    
    # We'll just sample a known "blue" area. 
    # Highlighting usually takes up a decent chunk of the image.
    # Let's try to find high-saturation blue areas.
    
    # Typical selection blue in the image:
    # Let's take a sample near the middle of the code block.
    # Based on the image, the highlight is around (y=400, x=400)
    sample = hsv[460:500, 400:450]
    
    h_mean = np.mean(sample[:,:,0])
    s_mean = np.mean(sample[:,:,1])
    v_mean = np.mean(sample[:,:,2])
    
    print(f"Sampled HSV Mean: H={h_mean:.1f}, S={s_mean:.1f}, V={v_mean:.1f}")
    print(f"Sampled HSV Min: {np.min(sample, axis=(0,1))}")
    print(f"Sampled HSV Max: {np.max(sample, axis=(0,1))}")

if __name__ == "__main__":
    import glob
    images = glob.glob("C:/Users/user/.gemini/antigravity/brain/71c788fd-08bc-4085-a373-d208af30422d/test_highlight_screen*.png")
    if images:
        analyze_blue_range(images[0])
