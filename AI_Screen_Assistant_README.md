# AI Screen Assistant

A Python desktop app that watches your clipboard. When you highlight any text in any application, it automatically sends that text to the Gemini API and displays the AI response in a fullscreen transparent overlay.

---

## Core Loop

```
User highlights text in any app (browser, IDE, PDF, terminal)
      ↓
Clipboard changes — detected by polling (pyperclip)
      ↓
Send text to Gemini 2.5 Flash API
      ↓
Display response in fullscreen transparent overlay (PyQt6)
      ↓
Wait for next clipboard change → repeat
```

---

## Tech Stack

| Category        | Library              |
|-----------------|----------------------|
| Clipboard Watch | pyperclip            |
| AI Model        | google-generativeai  |
| Desktop GUI     | PyQt6                |
| Config          | python-dotenv        |
| Packaging       | PyInstaller          |

---

## Installation

```bash
pip install pyperclip pyqt6 python-dotenv google-generativeai pyinstaller
```

---

## Environment Setup

```env
GEMINI_API_KEY=your_gemini_api_key_here
POLL_INTERVAL=0.3            # seconds between clipboard checks (default 0.3)
OVERLAY_OPACITY=0.15         # overlay panel background transparency (0.0–1.0)
OVERLAY_TEXT_SIZE=18         # font size in pixels
MIN_TEXT_LENGTH=3            # ignore clipboard changes shorter than this
MAX_TEXT_LENGTH=4000         # ignore clipboard changes longer than this
HOTKEY=<ctrl>+<shift>+p      # toggle overlay Active/Standby
```

---

## Project Structure

```
ai-screen-assistant/
│
├── main.py          # Entry point — starts clipboard watcher and overlay
├── clipboard.py     # Clipboard polling loop — detects text changes
├── vision.py        # Gemini API communication
├── overlay.py       # Fullscreen transparent overlay (PyQt6)
├── config.py        # Loads and exposes all .env values
├── hotkey.py        # Global hotkey listener — toggles Active/Standby
│
├── logs/
├── requirements.txt
├── .env
└── README.md
```

---

## Module Specifications

### `config.py`
Loads all values from `.env` using `python-dotenv`.

**Exports:**
```python
GEMINI_API_KEY: str
POLL_INTERVAL: float         # default: 0.3
OVERLAY_OPACITY: float       # default: 0.15
OVERLAY_TEXT_SIZE: int       # default: 18
MIN_TEXT_LENGTH: int         # default: 3
MAX_TEXT_LENGTH: int         # default: 4000
HOTKEY: str                  # default: "<ctrl>+<shift>+p"
```

---

### `clipboard.py`
Polls the clipboard every `POLL_INTERVAL` seconds. Fires a callback when the content changes and passes the new text.

**Function:**
```python
def watch_clipboard(on_change: callable, stop_event: threading.Event) -> None:
    # Loop until stop_event is set
    # Every POLL_INTERVAL seconds: call pyperclip.paste()
    # Strip whitespace from result
    # If result == last_seen: do nothing
    # If result is empty, or len < MIN_TEXT_LENGTH, or len > MAX_TEXT_LENGTH: do nothing
    # Otherwise: update last_seen, call on_change(text)
    # Never raise — catch all exceptions, log and continue
```

---

### `vision.py`
Sends the highlighted text to Gemini and returns the response.

**Function:**
```python
def analyze_text(text: str) -> str:
    # Initialize google.generativeai with GEMINI_API_KEY
    # Send text to gemini-2.5-flash with this system prompt:
    #   "You are a real-time assistant. The user has highlighted this text.
    #    If it is code: identify the language, explain what it does in 1–2 sentences,
    #    flag any obvious issues and suggest a fix.
    #    If it is an error message: explain the cause and give a concrete fix in 2–3 sentences.
    #    If it is plain text: summarize it in 1–2 sentences.
    #    Keep all responses under 80 words. Be direct and concise.
    #    Format your response as:
    #    WHAT: one line describing what this is
    #    ANSWER: your explanation or fix"
    # Return response.text as string
    # On any error: return "Could not analyze text."
```

---

### `overlay.py`
Fullscreen transparent always-on-top window. Passes all mouse and keyboard events through to apps beneath it.

**Class:**
```python
class OverlayWindow(QWidget):
    # Flags: Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint |
    #        Qt.Tool | Qt.WindowTransparentForInput
    # Geometry: full screen via QApplication.primaryScreen().geometry()
    # setAttribute(Qt.WA_TranslucentBackground, True)
    # setAttribute(Qt.WA_TransparentForMouseEvents, True)
    #
    # Layout: QVBoxLayout anchored to bottom of screen
    # Text panel: rounded rectangle (border-radius 12px), padding 16px
    # Panel background: rgba(0, 0, 0, OVERLAY_OPACITY)
    # QLabel: white, OVERLAY_TEXT_SIZE px, word-wrapped
    #
    # Two-line format rendered in panel:
    #   WHAT line: grey (#9ca3af), slightly smaller font
    #   ANSWER line: white, full size
    #
    # Status indicator: small QLabel top-right corner
    #   "● Active"  → #4ade80 (green), 12px
    #   "⏸ Standby" → #9ca3af (grey),  12px

    def update_text(self, what: str, answer: str) -> None:
        # Parse and render the two sections
        # Fade panel in via QPropertyAnimation (150ms) if hidden

    def clear_text(self) -> None:
        # Fade panel out (150ms) then hide

    def set_status(self, state: str) -> None:
        # state: "active" or "standby"
        # Update status indicator label and color
```

---

### `hotkey.py`
Global keyboard listener that toggles Active/Standby.

**Class:**
```python
class HotkeyManager:
    def __init__(self, on_toggle: callable):
        # Create pynput.keyboard.GlobalHotKeys({HOTKEY: on_toggle})

    def start(self) -> None:
        # Start listener as daemon thread

    def stop(self) -> None:
        # Stop listener
```

---

### `main.py`
Entry point. Wires clipboard watcher, Gemini API, overlay, and hotkey together.

**Behavior:**
```python
# 1. Create QApplication, TextSignal(QObject) with pyqtSignal(str, str)
# 2. Show OverlayWindow fullscreen, set_status("active")
# 3. Connect signal to overlay.update_text
# 4. Define on_clipboard_change(text):
#       if not is_active: return
#       signal.emit("Analyzing...", "")     # immediate loading feedback
#       threading.Thread(target=_analyze, args=(text,), daemon=True).start()
# 5. Define _analyze(text):
#       response = analyze_text(text)
#       what, answer = parse_response(response)   # split WHAT: / ANSWER:
#       signal.emit(what, answer)
# 6. Define parse_response(response) -> tuple[str, str]:
#       # Split on "ANSWER:" — first part is WHAT, second is ANSWER
#       # Strip labels and whitespace
#       # If format not found: return ("", response) — show full response as answer
# 7. Start clipboard watcher in daemon thread:
#       stop_event = threading.Event()
#       threading.Thread(target=watch_clipboard,
#                        args=(on_clipboard_change, stop_event),
#                        daemon=True).start()
# 8. Wire hotkey toggle:
#       def on_toggle():
#           is_active = not is_active
#           overlay.set_status("active" if is_active else "standby")
#           if not is_active: overlay.clear_text()
# 9. HotkeyManager(on_toggle=on_toggle).start()
# 10. app.exec() — blocks main thread; Ctrl+C exits cleanly
```

---

## Build & Package

```bash
pyinstaller --onefile --windowed --name "AI-Screen-Assistant" main.py
```

The `.env` file must sit alongside the binary at runtime.

---

## Development Phases

### Phase 1 — MVP
All 6 modules implemented to spec. Highlight text → overlay responds.

### Phase 2 — Polish
- Auto-clear overlay after N seconds of no new highlight (`AUTO_CLEAR_SECONDS` env var)
- Smooth fade-in/out animations on panel
- Loading spinner while API call is in flight

### Phase 3 — Expansion
- Multi-language support in the system prompt
- Response history (last 3 highlights accessible via hotkey cycle)
- Optional screenshot context: attach a screen region alongside the text for richer analysis