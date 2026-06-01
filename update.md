# AI Screen Assistant — Update v2

This document is a delta update on top of the existing codebase. Apply every change listed here in order. Do not touch any module not mentioned. Keep all existing behavior intact unless a section explicitly says to replace it.

---

## New Dependencies

Add these to `requirements.txt` and install before making any code changes:

```bash
pip install pynput pyperclip
```

| Library    | Purpose                              |
|------------|--------------------------------------|
| `pynput`   | Global hotkey listener               |
| `pyperclip`| Read highlighted/selected text from clipboard |

---

## New Environment Variables

Append these to `.env` and add them to `config.py`:

```env
HOTKEY=<ctrl>+<shift>+space  # pynput key combo string to toggle assistant on/off
AUTO_PAUSE_SECONDS=30        # seconds of inactivity before assistant auto-pauses (0 = disabled)
```

### `config.py` — append exports
```python
HOTKEY: str                  # default: "<ctrl>+<shift>+space"
AUTO_PAUSE_SECONDS: int      # default: 30
```

---

## Change 1 — Highlighted Text Context (`utils.py`)

**What:** Instead of full-screen OCR, read the system clipboard after each capture. If the clipboard contains plain text (i.e. the user has highlighted something), prepend it to the API prompt as context. Zero processing overhead — no OCR library needed.

**Why:** Highlighted text is the most precise signal of what the user wants explained. Clipboard reading is near-instant vs `pytesseract` which adds 300–800ms per frame.

**How to implement — add to `utils.py`:**

```python
def get_highlighted_text() -> str | None:
    # Use pyperclip.paste() to read clipboard contents
    # Strip whitespace from result
    # Return the string if it is non-empty and len <= 2000 characters
    # Return None if clipboard is empty, non-text, or exceeds length limit
    # Never raise — catch all exceptions and return None
```

**How it plugs into `vision.py` — update `analyze_screenshot`:**

```python
def analyze_screenshot(base64_image: str, highlighted_text: str | None = None) -> str:
    # If highlighted_text is not None, prepend this block to the prompt:
    #   "The user has highlighted this text on screen:\n\"{highlighted_text}\"\n
    #    Focus your analysis on this selection specifically."
    # Then append the existing system prompt instructions as-is
    # Everything else in the function stays the same
```

**How it plugs into `main.py` capture loop:**
```python
# After encode_image_to_base64() and before executor.submit():
highlighted = get_highlighted_text()
future = executor.submit(analyze_screenshot, b64, highlighted)
```

---

## Change 2 — Hotkey Toggle (`hotkey.py`) — new file

**What:** A global keyboard listener that toggles the assistant between **Active** and **Standby** states using `pynput`. This is a new module — create `hotkey.py`.

**Why:** Gives the user direct control over API usage. In Standby, zero captures and zero API calls happen. Essential for quota management.

```python
# hotkey.py

from pynput import keyboard
from config import HOTKEY

class HotkeyManager:
    # Wraps a pynput GlobalHotKeys listener
    # Takes a callback function on_toggle() called every time the hotkey fires

    def __init__(self, on_toggle: callable):
        # Parse HOTKEY string (e.g. "<ctrl>+<shift>+space") into pynput format
        # Create keyboard.GlobalHotKeys({HOTKEY: on_toggle})
        # Store listener as self._listener

    def start(self) -> None:
        # Start self._listener in a daemon thread (listener.start())

    def stop(self) -> None:
        # Call self._listener.stop()
```

**Add to project structure:**
```
├── hotkey.py        # Global hotkey listener — toggles Active/Standby
```

---

## Change 3 — Active/Standby State + Auto-Pause (`main.py`)

**What:** Wire the hotkey and auto-pause into the main capture loop. The assistant now has two states: **Active** (captures and calls API) and **Standby** (dormant, no API calls). Auto-pause triggers after `AUTO_PAUSE_SECONDS` of the assistant being idle in Standby.

**Replace the `capture_loop` function in `main.py` with this logic:**

```python
# State
is_active: bool = True          # starts Active on launch
last_active_time: float = time.time()

def on_hotkey_toggle():
    global is_active
    is_active = not is_active
    if is_active:
        last_active_time = time.time()
        overlay.show()
        signal.emit("▶ Assistant active")
    else:
        signal.emit("⏸ Assistant paused")
        # After 1.5s delay, call overlay.clear_text() then overlay.hide()

def capture_loop():
    global is_active, last_active_time
    with ThreadPoolExecutor(max_workers=2) as executor:
        while True:
            if not is_active:
                # Auto-pause: if manually paused longer than AUTO_PAUSE_SECONDS, stay dormant
                time.sleep(0.2)    # idle poll — keep CPU near zero
                continue

            start       = time.time()
            image       = capture_screen()
            b64         = encode_image_to_base64(image)
            highlighted = get_highlighted_text()
            future      = executor.submit(analyze_screenshot, b64, highlighted)
            text        = future.result()
            signal.emit(text)

            elapsed = time.time() - start
            time.sleep(max(0, CAPTURE_INTERVAL - elapsed))

# In main():
hotkey_manager = HotkeyManager(on_toggle=on_hotkey_toggle)
hotkey_manager.start()
```

---

## Change 4 — Overlay Status Line (`overlay.py`)

**What:** Add a small persistent status indicator in the top-right corner of the overlay showing current state: `● Active` (green) or `⏸ Standby` (grey). This is a secondary label — it does not replace the main response panel.

**Add to `OverlayWindow`:**

```python
def set_status(self, state: str) -> None:
    # state is either "active" or "standby"
    # Updates a small QLabel in the top-right corner (fixed position, 12px, semi-transparent)
    # "active"  → text "● Active",  color #4ade80 (green)
    # "standby" → text "⏸ Standby", color #9ca3af (grey)
```

**Wire it in `main.py`:**
```python
# Call overlay.set_status("active") on launch
# Call overlay.set_status("standby") inside on_hotkey_toggle when pausing
# Call overlay.set_status("active") inside on_hotkey_toggle when resuming
```

---

## Updated Core Loop (v2)

```
Hotkey Active?
      │ No  → idle sleep 0.2s → check again
      │ Yes
      ↓
Capture Screen (MSS + OpenCV resize)
      ↓
Read Clipboard (pyperclip) — highlighted text if any
      ↓
Encode to Base64 JPEG
      ↓
Submit to ThreadPoolExecutor → Gemini 2.5 Flash API
      ↓
Parse response + inject highlighted context if present
      ↓
Emit Qt signal → Update fullscreen overlay
      ↓
Respect CAPTURE_INTERVAL throttle floor → repeat
```

---

## Notes

| Decision | Reason |
|---|---|
| No diff method | Every frame goes straight to the API — no per-frame comparison overhead, no added latency. Hotkey and auto-pause handle quota control instead |
| `AUTO_PAUSE_SECONDS` | Passively guards quota — if the user forgets to pause, the assistant sleeps itself after idle |
| `HOTKEY` in `.env` | User-configurable without touching code |
| Status indicator in overlay | User always knows if the assistant is active and consuming quota |
| Clipboard length cap (2000 chars) | Prevents accidental massive pastes inflating the prompt and slowing the API call |

---

## File Change Summary

| File | Change Type | Summary |
|---|---|---|
| `config.py` | Append | 2 new exports: `HOTKEY`, `AUTO_PAUSE_SECONDS` |
| `utils.py` | Append | `get_highlighted_text()` via pyperclip |
| `vision.py` | Modify | `highlighted_text` optional param injected into prompt |
| `overlay.py` | Append | `set_status()` with top-right status indicator |
| `hotkey.py` | New file | `HotkeyManager` class wrapping pynput GlobalHotKeys |
| `main.py` | Modify | Rewire capture loop with Active/Standby state and hotkey |
| `requirements.txt` | Append | `pynput`, `pyperclip` |