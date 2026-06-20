import sys
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

import config
import clipboard
import hotkey
from vision import analyze_text
from overlay import OverlayWindow

# Global state
is_active = True


class TextSignal(QObject):
    """Thread-safe signal for updating the overlay from background threads."""
    update_signal = pyqtSignal(str, str, str)


def parse_response(response: str) -> tuple[str, str, str]:
    """
    Splits the Gemini response into ISSUE, EXPLANATION, SOLUTION.
    Returns ("", "", full_response) if the format is not found.
    """
    issue = explanation = solution = ""

    try:
        text = response.strip()

        def extract(label: str, next_labels: list[str]) -> str:
            label_upper = label.upper() + ":"
            start = text.upper().find(label_upper)
            if start == -1:
                return ""
            start += len(label_upper)
            end = len(text)
            for nxt in next_labels:
                nxt_pos = text.upper().find(nxt.upper() + ":", start)
                if nxt_pos != -1:
                    end = min(end, nxt_pos)
            return text[start:end].strip()

        issue       = extract("ISSUE",       ["EXPLANATION", "SOLUTION"])
        explanation = extract("EXPLANATION", ["SOLUTION"])
        solution    = extract("SOLUTION",    [])

    except Exception:
        pass

    if not any([issue, explanation, solution]):
        return ("", "", response.strip())

    return issue, explanation, solution


def main():
    global is_active

    app = QApplication(sys.argv)

    # 1. Initialize signal and overlay
    signal_obj = TextSignal()
    overlay = OverlayWindow()
    overlay.showFullScreen()
    overlay.set_status("active")

    # 2. Connect signal to overlay
    signal_obj.update_signal.connect(overlay.update_text)

    # 3. Define _analyze inside main so it closes over signal_obj
    def _analyze(text: str):
        response = analyze_text(text)
        issue, explanation, solution = parse_response(response)
        signal_obj.update_signal.emit(issue, explanation, solution)

    def on_clipboard_change(text: str):
        if not is_active:
            return
        overlay.show_loading()
        threading.Thread(target=_analyze, args=(text,), daemon=True).start()

    def on_hotkey_toggle():
        global is_active
        is_active = not is_active
        overlay.set_status("active" if is_active else "standby")
        if not is_active:
            overlay.clear_text()

    # 4. Start clipboard watcher
    stop_event = threading.Event()
    threading.Thread(
        target=clipboard.watch_clipboard,
        args=(on_clipboard_change, stop_event),
        daemon=True
    ).start()

    # 5. Start hotkey manager
    hk_manager = hotkey.HotkeyManager(on_toggle=on_hotkey_toggle)
    hk_manager.start()

    # 6. Run application
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        stop_event.set()
        hk_manager.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()