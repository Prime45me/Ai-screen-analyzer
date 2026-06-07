import time
import vision
import pyperclip
import threading

def test_api():
    print("Testing vision.py directly...")
    
    code = "def is_even(n): return n % 2 == 0"
    print("\n[VISION] Sending Code:")
    res_code = vision.analyze_text(code)
    print(res_code)
    
    err = "Exception in Tkinter callback\nTraceback (most recent call last):\nValueError: bad window path name"
    print("\n[VISION] Sending Error:")
    res_err = vision.analyze_text(err)
    print(res_err)
    
    text = "The quick brown fox jumps over the lazy dog."
    print("\n[VISION] Sending Text:")
    res_text = vision.analyze_text(text)
    print(res_text)

if __name__ == "__main__":
    test_api()
