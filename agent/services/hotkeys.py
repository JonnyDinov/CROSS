from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict

try:
    import keyboard
except ImportError:  # pragma: no cover
    keyboard = None

from agent.config import config


@dataclass
class HotkeyAction:
    name: str
    combo: str
    callback: Callable[[], None]


class HotkeyService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._actions: Dict[str, HotkeyAction] = {}
        self._listener_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def register_action(self, name: str, combo: str, callback: Callable[[], None]):
        self._actions[name] = HotkeyAction(name, combo, callback)
        if keyboard:
            try:
                keyboard.add_hotkey(combo, callback)
                self.logger.info("Registered hotkey %s -> %s", combo, name)
            except Exception as e:
                self.logger.error("Failed to register hotkey %s: %s", combo, e)

    def unregister_all(self):
        if keyboard:
            keyboard.clear_all_hotkeys()
        self._actions.clear()

    def start(self):
        if keyboard is None:
            self.logger.warning("Keyboard module not available. Hotkeys disabled.")
            return

        if self._listener_thread and self._listener_thread.is_alive():
            return

        self._stop_event.clear()
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()
        self.logger.info("Hotkey listener started")

    def stop(self):
        self._stop_event.set()
        if self._listener_thread:
            self._listener_thread.join(timeout=1)
        if keyboard:
            keyboard.clear_all_hotkeys()
        self.logger.info("Hotkey listener stopped")

    def _listen_loop(self):
        while not self._stop_event.is_set():
            time.sleep(0.1)

    def load_from_config(self, prompt_callback: Callable[[], None], text_callback: Callable[[], None]):
        prompt_combo = config.get("hotkeys.prompt_panel", "ctrl+p")
        text_combo = config.get("hotkeys.text_processing", "ctrl+e")
        self.register_action("prompt_panel", prompt_combo, prompt_callback)
        self.register_action("text_processing", text_combo, text_callback)


hotkey_service = HotkeyService()
