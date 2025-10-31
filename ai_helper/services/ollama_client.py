from __future__ import annotations

import json
from typing import Any

import httpx

from ai_helper.config import OLLAMA_MODEL, OLLAMA_URL


class OllamaClient:
    def __init__(self, url: str = OLLAMA_URL, model: str = OLLAMA_MODEL, timeout: float = 60.0) -> None:
        self.url = url
        self.model = model
        self.timeout = timeout

    def chat(
        self,
        system_prompt: str,
        user_prompt: str | None = None,
        messages: list[dict[str, str]] | None = None,
    ) -> str:
        conversation: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if messages:
            conversation.extend(messages)
        if user_prompt:
            conversation.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model,
            "messages": conversation,
            "stream": False,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.url, json=payload)
            response.raise_for_status()

        data = response.json()
        return data.get("message", {}).get("content", "").strip()


__all__ = ["OllamaClient"]
