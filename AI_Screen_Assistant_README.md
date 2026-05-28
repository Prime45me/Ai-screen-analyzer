# AI Screen Assistant

A Python desktop application that continuously captures the screen, sends screenshots to the Gemini Vision API, and displays AI-generated responses in a fullscreen transparent overlay — always on top, never blocking interaction, updating as fast as the API allows.

---

## Core Loop

```
Capture Screen (MSS) ──→ Resize to 50% (OpenCV) ──→ Encode to Base64 JPEG (quality 70)
                                                              ↓
                                              POST to Gemini 2.5 Flash Vision API
                                                              ↓
                                                  Parse AI text response (streaming)
                                                              ↓
                                              Update fullscreen overlay (PyQt6 signal)
                                                              ↓
                                              Immediately capture next frame → repeat
```

> Capture and API call run in parallel using a thread pool. The overlay updates the moment a response arrives — no fixed wait interval.

---

## Tech Stack

| Category        | Library              | Version  |
|-----------------|----------------------|----------|
| Screen Capture  | mss                  | latest   |
| Image Processing| Pillow               | latest   |
| Computer Vision | opencv-python        | latest   |
| AI Vision Model | google-generativeai  | latest   |
| Desktop GUI     | PyQt6                | latest   |
| Config          | python-dotenv        | latest   |
| Packaging       | PyInstaller          | latest   |

---

## Installation

```bash
pip install mss opencv-python pyqt6 pillow python-dotenv google-generativeai pyinstaller
```

---

## Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
CAPTURE_INTERVAL=2            # minimum seconds between API calls (throttle floor)
OVERLAY_OPACITY=0.15          # float 0.0–1.0; low value keeps screen readable
OVERLAY_TEXT_SIZE=18          # font size in px for the overlay response text
IMAGE_RESIZE_FACTOR=0.5       # downscale factor before encoding (0.5 = half resolution)
IMAGE_JPEG_QUALITY=70         # JPEG compression quality (lower = faster upload)
```

---

## Project Structure

```
ai-screen-assistant/
│
├── main.py          # Entry point — starts the capture loop and overlay
├── capture.py       # Screen capture and image pre-processing
├── vision.py        # Gemini API communication
├── overlay.py       # Fullscreen transparent pass-through overlay (PyQt6)
├── config.py        # Loads and exposes all .env values
├── utils.py         # Shared helpers: logging, image encoding
│
├── screenshots/     # Temporarily saved screenshots (auto-cleared)
├── logs/            # Runtime logs
│
├── requirements.txt
├── .env
└── README.md
```

---

## Module Specifications

### `config.py`
Loads all environment variables from `.env` using `python-dotenv`.

**Exports:**
```python
GEMINI_API_KEY: str
CAPTURE_INTERVAL: int        # default: 2
OVERLAY_OPACITY: float       # default: 0.15
OVERLAY_TEXT_SIZE: int       # default: 18
IMAGE_RESIZE_FACTOR: float   # default: 0.5
IMAGE_JPEG_QUALITY: int      # default: 70
```

---

### `capture.py`
Captures the primary monitor screenshot using MSS, downsizes it with OpenCV, and returns it as a Pillow Image.

**Function:**
```python
def capture_screen() -> PIL.Image.Image
    # Uses mss to grab the full primary monitor
    # Converts raw pixel data to a NumPy array (BGR via OpenCV)
    # Resizes by IMAGE_RESIZE_FACTOR using cv2.resize with INTER_AREA interpolation
    # Converts result to Pillow Image (RGB)
    # Returns the Image object — does NOT save to disk
```

---

### `utils.py`
Encodes a Pillow Image to a Base64 JPEG string for API transmission.

**Function:**
```python
def encode_image_to_base64(image: PIL.Image.Image) -> str
    # Saves image to an in-memory BytesIO buffer as JPEG at IMAGE_JPEG_QUALITY
    # Base64-encodes the buffer
    # Returns the encoded string
```

**Also includes:**
```python
def setup_logger(name: str) -> logging.Logger
    # Creates a logger writing to logs/app.log and stdout
    # Log format: [TIMESTAMP] [LEVEL] message
```

---

### `vision.py`
Sends the encoded screenshot to the Gemini 2.5 Flash Vision API and returns the AI response text.

**Function:**
```python
def analyze_screenshot(base64_image: str) -> str
    # Initializes google.generativeai with GEMINI_API_KEY
    # Builds an inline image part from the base64 JPEG
    # Sends to model: gemini-2.5-flash with this system prompt:
    #   "You are a real-time screen assistant. Analyze the screenshot.
    #    If there is an error, explain it clearly and suggest a fix in 2–3 sentences.
    #    If there is code visible: first identify the language, then explain in 1–2 sentences
    #    what the code does — focus on its purpose and output, not line-by-line detail.
    #    If it is a tutorial or workflow, summarize the current step.
    #    Keep all responses under 60 words. Be direct and concise."
    # Returns response.text (string)
    # On API error: returns "Could not analyze screen."
```

---

### `overlay.py`
Renders a fullscreen transparent always-on-top overlay. The window covers the entire screen but passes all mouse and keyboard events through to the apps beneath it — the user can interact with their desktop normally while the overlay is active.

**Class:**
```python
class OverlayWindow(QWidget):
    # Window flags:
    #   Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint |
    #   Qt.Tool | Qt.WindowTransparentForInput
    # Geometry: full screen (QApplication.primaryScreen().geometry())
    # Background: fully transparent window; text panel uses rgba(0, 0, 0, OVERLAY_OPACITY)
    # Layout: QVBoxLayout anchored to the bottom of the screen
    # Text panel: rounded rectangle (border-radius 12px), padding 16px
    # QLabel inside panel: white, OVERLAY_TEXT_SIZE px, word-wrapped, max-width 60% of screen
    # setAttribute(Qt.WA_TranslucentBackground, True)
    # setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def update_text(self, text: str) -> None:
        # Updates QLabel text
        # Shows the text panel if hidden
        # Fades panel in using QPropertyAnimation on windowOpacity (150ms ease-in)

    def clear_text(self) -> None:
        # Fades panel out (150ms), then hides it
```

---

### `main.py`
Entry point. Starts the PyQt6 application and drives the capture → analyze → display loop using a `ThreadPoolExecutor` for non-blocking API calls.

**Behavior:**
```python
# 1. Initialize QApplication and show OverlayWindow (fullscreen)
# 2. Define TextUpdateSignal(QObject) with a pyqtSignal(str) for thread-safe overlay updates
# 3. Start a daemon threading.Thread running capture_loop()
# 4. capture_loop() uses concurrent.futures.ThreadPoolExecutor(max_workers=2):
#      while True:
#          image  = capture_screen()
#          b64    = encode_image_to_base64(image)
#          future = executor.submit(analyze_screenshot, b64)
#          text   = future.result()           # blocks only this thread, not the UI
#          signal.emit(text)                  # → overlay.update_text(text) on main thread
#          time.sleep(max(0, CAPTURE_INTERVAL - elapsed))  # respect throttle floor
# 5. If API call takes longer than CAPTURE_INTERVAL, next capture starts immediately after result
# 6. app.exec() blocks main thread; Ctrl+C and window close exit cleanly
```

---

## Build & Package

```bash
pyinstaller --onefile --windowed --name "AI-Screen-Assistant" main.py
```

Output binary is in `dist/`. The `.env` file must be placed alongside the binary at runtime.

---

## Development Phases

### Phase 1 — MVP
Implement all 6 modules to their specifications above. The app should capture, analyze, and display responses in the overlay on each interval tick.

### Phase 2 — Overlay & Performance
- Replace polling loop with a diff-based trigger: only call the API when the screenshot has changed by more than a threshold (compare frames with OpenCV `cv2.absdiff`)
- Add a visual loading indicator in the overlay while the API call is in flight
- Debounce rapid screen changes to avoid redundant API calls

### Phase 3 — Context & Accuracy
- Maintain a 3-frame rolling history; include the previous response as context in the next API prompt
- Add OCR pre-pass using `pytesseract` to extract visible text and append it to the image payload for higher accuracy on code and error messages