import sys
import time
import threading
import signal
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

import config
import capture
import utils
import vision
from overlay import OverlayWindow
from hotkey import HotkeyManager

# Signal wrapper class for thread-safe UI updates
class TextUpdateSignal(QObject):
    update_text_signal = pyqtSignal(str)

# -------------------------------------------------------------------
# Module-level state (shared between capture_loop and on_hotkey_toggle)
# -------------------------------------------------------------------
is_active: bool = True
last_active_time: float = time.time()

# References set in main() before the loop thread starts
_overlay: OverlayWindow = None
_signal_obj: TextUpdateSignal = None


def on_hotkey_toggle():
    """Toggle between Active and Standby states."""
    global is_active, last_active_time
    is_active = not is_active
    if is_active:
        last_active_time = time.time()
        _overlay.show()
        _overlay.set_status("active")
        _signal_obj.update_text_signal.emit("▶ Assistant active")
    else:
        _overlay.set_status("standby")
        _signal_obj.update_text_signal.emit("⏸ Assistant paused")
        # After 1.5s fade-out delay, clear and hide the panel
        def _deferred_hide():
            time.sleep(1.5)
            _signal_obj.update_text_signal.emit("")  # triggers clear_text via ''
        threading.Thread(target=_deferred_hide, daemon=True).start()


def capture_loop():
    """
    Background loop: captures screen, reads clipboard, sends to Gemini, updates overlay.
    When is_active is False, idles at 0.2s poll to keep CPU near zero.
    """
    logger = utils.setup_logger("App")
    logger.info("Application starting...")

    global is_active, last_active_time

    with ThreadPoolExecutor(max_workers=2) as executor:
        while True:
            try:
                if not is_active:
                    # Auto-pause: simply poll until toggled back on
                    time.sleep(0.2)
                    continue

                start = time.time()

                # 1. Capture and encode image
                logger.info("Capturing screen...")
                image = capture.capture_screen()
                b64 = utils.encode_image_to_base64(image)

                # 2. Read clipboard for highlighted text context
                highlighted = utils.get_highlighted_text()

                # 3. Submit to thread pool
                logger.info("Sending to API...")
                future = executor.submit(vision.analyze_screenshot, image, highlighted)
                text = future.result()

                # 4. Emit text to overlay
                logger.info(f"Analysis complete: {text[:50]}...")
                _signal_obj.update_text_signal.emit(text)

                # 5. Respect capture interval throttle
                elapsed = time.time() - start
                time.sleep(max(0, config.CAPTURE_INTERVAL - elapsed))

            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                time.sleep(config.CAPTURE_INTERVAL)


def main():
    global _overlay, _signal_obj

    # Allow terminal interruption
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 1. Initialize QApplication
    app = QApplication(sys.argv)

    # 2. Create signal object
    _signal_obj = TextUpdateSignal()

    # 3. Initialize and show OverlayWindow fullscreen
    _overlay = OverlayWindow()
    _overlay.showFullScreen()

    # 4. Set initial status
    _overlay.set_status("active")

    # 5. Connect signal to overlay update_text (empty string calls clear_text)
    def _handle_update(text: str):
        if text:
            _overlay.update_text(text)
        else:
            _overlay.clear_text()

    _signal_obj.update_text_signal.connect(_handle_update)

    # 6. Wire hotkey manager
    hotkey_manager = HotkeyManager(on_toggle=on_hotkey_toggle)
    hotkey_manager.start()

    # 7. Start capture loop in daemon thread
    loop_thread = threading.Thread(target=capture_loop, daemon=True)
    loop_thread.start()

    # 8. Block on application event loop
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        hotkey_manager.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
