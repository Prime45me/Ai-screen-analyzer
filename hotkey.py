from pynput import keyboard
import config

class HotkeyManager:
    """
    Global keyboard listener using pynput to toggle the assistant state.
    """
    def __init__(self, on_toggle: callable):
        # Configure the global hotkey based on string from config
        self._listener = keyboard.GlobalHotKeys({
            config.HOTKEY: on_toggle
        })

    def start(self) -> None:
        """Starts the listener in a daemon thread."""
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        """Stops the listener."""
        self._listener.stop()
