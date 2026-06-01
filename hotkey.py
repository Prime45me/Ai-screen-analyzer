# hotkey.py
# Global hotkey listener — toggles Active/Standby state via pynput.

from pynput import keyboard
from config import HOTKEY


def _normalise_hotkey(hotkey_str: str) -> str:
    """
    Normalise a hotkey string so every token is wrapped in angle brackets.
    e.g. "<ctrl>+<shift>+space" -> "<ctrl>+<shift>+<space>"
    Tokens that are already wrapped (start with '<') are left as-is.
    """
    parts = hotkey_str.split("+")
    normalised = []
    for part in parts:
        part = part.strip()
        if part.startswith("<") and part.endswith(">"):
            normalised.append(part)
        else:
            normalised.append(f"<{part}>")
    return "+".join(normalised)


class HotkeyManager:
    """
    Wraps a pynput GlobalHotKeys listener.
    Calls on_toggle() every time the configured hotkey fires.
    """

    def __init__(self, on_toggle: callable):
        # Normalise the HOTKEY string before passing to pynput
        normalised = _normalise_hotkey(HOTKEY)
        self._listener = keyboard.GlobalHotKeys({normalised: on_toggle})

    def start(self) -> None:
        """Start the listener in a daemon thread."""
        self._listener.start()

    def stop(self) -> None:
        """Stop the listener."""
        self._listener.stop()
