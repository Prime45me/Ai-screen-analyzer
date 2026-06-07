import time
import threading
import pyperclip
import config

def watch_clipboard(on_change: callable, stop_event: threading.Event) -> None:
    """
    Poll pyperclip.paste() every POLL_INTERVAL seconds.
    Detects changes in clipboard text and fires on_change callback.
    """
    last_seen = ""
    
    while not stop_event.is_set():
        try:
            # Read clipboard contents
            text = pyperclip.paste()
            
            if not isinstance(text, str):
                time.sleep(config.POLL_INTERVAL)
                continue
                
            text = text.strip()
            
            # Validation logic
            if text == last_seen:
                pass
            elif not text:
                pass
            elif len(text) < config.MIN_TEXT_LENGTH:
                pass
            elif len(text) > config.MAX_TEXT_LENGTH:
                pass
            else:
                # Valid new text detected
                last_seen = text
                on_change(text)
                
        except Exception as e:
            # Catch all exceptions, log but continue the loop
            print(f"Clipboard Watcher Error: {e}")
            
        time.sleep(config.POLL_INTERVAL)
