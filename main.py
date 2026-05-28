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

# Signal wrapper class for thread-safe UI updates
class TextUpdateSignal(QObject):
    update_text_signal = pyqtSignal(str)

def capture_loop(signal_obj):
    """
    Background loop that handles screen capture, vision analysis, and signaling.
    Uses a ThreadPoolExecutor for vision analysis tasks.
    """
    logger = utils.setup_logger("App")
    logger.info("Application starting...")
    
    # Executor for vision tasks
    executor = ThreadPoolExecutor(max_workers=2)
    
    prev_image = None
    
    while True:
        try:
            start_time = time.time()
            
            # 1. Capture and downscale image
            logger.info("Capturing screen...")
            image = capture.capture_screen()
            
            # 2. Check if screen changed enough to warrant an API call
            if not utils.has_screen_changed(prev_image, image, threshold=2.0):
                logger.info("Screen hasn't changed significantly. Skipping API call.")
                
                # Sleep and continue
                elapsed = time.time() - start_time
                time.sleep(max(0, config.CAPTURE_INTERVAL - elapsed))
                continue
                
            prev_image = image
            
            # 3. Submit image directly to executor for Vision API analysis
            logger.info("Sending to Vision API...")
            future = executor.submit(vision.analyze_screenshot, image)
            text = future.result()
            
            # 4. Emit the parsed text to the overlay
            logger.info(f"Analysis complete: {text[:50]}...")
            signal_obj.update_text_signal.emit(text)
            
            # 5. Timing logic: ensures interval between captures
            elapsed = time.time() - start_time
            sleep_duration = max(0, config.CAPTURE_INTERVAL - elapsed)
            
            if sleep_duration > 0:
                time.sleep(sleep_duration)
                
        except Exception as e:
            logger.error(f"Error in capture loop: {e}")
            time.sleep(config.CAPTURE_INTERVAL)

def main():
    # Allow terminal interruption
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 1. Initialize QApplication
    app = QApplication(sys.argv)
    
    # 2. Create signal object
    signal_obj = TextUpdateSignal()
    
    # 3. Initialize and show OverlayWindow fullscreen
    overlay = OverlayWindow()
    overlay.showFullScreen()
    
    # 4. Connect signal to overlay method
    signal_obj.update_text_signal.connect(overlay.update_text)
    
    # 5. Start capture loop in daemon thread
    loop_thread = threading.Thread(target=capture_loop, args=(signal_obj,), daemon=True)
    loop_thread.start()
    
    # 6. Block on application event loop
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
