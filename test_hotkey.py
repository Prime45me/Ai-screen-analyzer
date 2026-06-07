import time
from pynput.keyboard import Controller, Key

def test():
    keyboard = Controller()
    print("Pressing keys...")
    keyboard.press(Key.ctrl)
    keyboard.press(Key.shift)
    keyboard.press(Key.space)
    
    keyboard.release(Key.space)
    keyboard.release(Key.shift)
    keyboard.release(Key.ctrl)
    print("Keys released!")
    
if __name__ == "__main__":
    test()
