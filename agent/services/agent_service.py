from __future__ import annotations

import logging
import threading
import time
from typing import Optional

from agent.config import config
from agent.core.agent import agent
from agent.core.logging import configure_logging
from agent.services.hotkeys import hotkey_service

class AgentService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._running:
            return

        configure_logging(config.get("agent.log_level", "INFO"))
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        hotkey_service.load_from_config(self._on_prompt_hotkey, self._on_text_hotkey)
        hotkey_service.start()

        self.logger.info("Agent service started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        hotkey_service.stop()
        self.logger.info("Agent service stopped")

    def _run(self):
        update_frequency = config.get("agent.update_frequency", 1.0)
        while self._running:
            try:
                time.sleep(update_frequency)
            except Exception as e:
                self.logger.error("Service loop error: %s", e)
                time.sleep(1)

    def _on_prompt_hotkey(self):
        self.logger.info("Prompt hotkey activated")
        # Placeholder: Integrate with GUI or CLI

    def _on_text_hotkey(self):
        self.logger.info("Text processing hotkey activated")
        try:
            import pyperclip
            selected_text = pyperclip.paste()
            if selected_text:
                response = agent.process_text(selected_text, "Process the selected text")
                pyperclip.copy(response)
                self.logger.info("Processed text copied to clipboard")
        except Exception as e:
            self.logger.error("Failed to process clipboard text: %s", e)


def run_service():
    service = AgentService()
    service.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()

