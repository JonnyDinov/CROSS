from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Callable, Optional

try:
    from pynput import keyboard
except ImportError:  # pragma: no cover - optional dependency
    keyboard = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class HotkeyCallbacks:
    quick_editor: Callable[[], None]
    main_menu: Callable[[], None]


class GlobalHotkeyListener:
    def __init__(self, callbacks: HotkeyCallbacks) -> None:
        self.callbacks = callbacks
        self.listener: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if keyboard is None:
            logger.warning("pynput is not installed; global hotkeys are disabled.")
            return
        if self.listener and self.listener.is_alive():
            return

        def run_listener() -> None:
            with keyboard.GlobalHotKeys({
                "<alt>+w": self.callbacks.quick_editor,
                "<alt>+f": self.callbacks.main_menu,
            }) as hotkeys:
                while not self._stop_event.is_set():
                    hotkeys.join(0.1)

        self.listener = threading.Thread(target=run_listener, daemon=True)
        self.listener.start()

    def stop(self) -> None:
        self._stop_event.set()


__all__ = ["GlobalHotkeyListener", "HotkeyCallbacks"]
