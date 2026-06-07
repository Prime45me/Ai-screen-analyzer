import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

import config
import clipboard
import vision
import hotkey
from overlay import OverlayWindow

# Global state
is_active = True

class TextSignal(QObject):
    """Thread-safe signal for updating the overlay from background threads."""
    update_signal = pyqtSignal(str, str)

def parse_response(response: str) -> tuple[str, str]:
    """
    Splits the AI response into 'WHAT' and 'ANSWER' sections.
    Expected format: 
    WHAT: ...
    ANSWER: ...
    """
    if "ANSWER:" in response:
        parts = response.split("ANSWER:", 1)
        what = parts[0].replace("WHAT:", "").strip()
        answer = parts[1].strip()
        return what, answer
    return "", response

def _analyze(text: str, signal_obj: TextSignal):
    """Background worker for API communication."""
    response = vision.analyze_text(text)
    what, answer = parse_response(response)
    signal_obj.update_signal.emit(what, answer)

def main():
    global is_active
    
    app = QApplication(sys.argv)
    
    # 1. Initialize Signal and Overlay
    signal_obj = TextSignal()
    overlay = OverlayWindow()
    overlay.showFullScreen()
    overlay.set_status("active")
    
    # 2. Connect Signal to UI
    signal_obj.update_signal.connect(overlay.update_text)
    
    def on_clipboard_change(text: str):
        if not is_active:
            return
        # Immediate loading feedback
        signal_obj.update_signal.emit("Analyzing...", "")
        # Run analysis in a background thread to keep UI responsive
        threading.Thread(target=_analyze, args=(text, signal_obj), daemon=True).start()
        
    def on_hotkey_toggle():
        global is_active
        is_active = not is_active
        overlay.set_status("active" if is_active else "standby")
        if not is_active:
            overlay.clear_text()
            
    # 3. Start Clipboard Watcher
    stop_event = threading.Event()
    watcher_thread = threading.Thread(
        target=clipboard.watch_clipboard,
        args=(on_clipboard_change, stop_event),
        daemon=True
    )
    watcher_thread.start()
    
    # 4. Start Hotkey Manager
    hk_manager = hotkey.HotkeyManager(on_toggle=on_hotkey_toggle)
    hk_manager.start()
    
    # 5. Run Application
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        stop_event.set()
        hk_manager.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
