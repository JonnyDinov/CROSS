import requests
from typing import Optional, Dict, List, Any
from PyQt5.QtCore import QThread, pyqtSignal


class OllamaClient:
    def __init__(self, api_url: str = "http://localhost:11434", model: str = "llama2"):
        self.api_url = api_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        url = f"{self.api_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(data["error"])

        text = data.get("response")
        if not text:
            message = data.get("message")
            if isinstance(message, dict):
                text = message.get("content")
        if not text:
            raise RuntimeError("Пустой ответ от Ollama")
        return text

    def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.api_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(data["error"])

        message = data.get("message", {})
        text = message.get("content") if isinstance(message, dict) else None
        if not text:
            # Некоторые модели возвращают поле `response`
            text = data.get("response")
        if not text:
            raise RuntimeError("Пустой ответ от Ollama")
        return text

    def get_available_models(self) -> List[str]:
        try:
            url = f"{self.api_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            models = result.get("models", [])
            return [model["name"] for model in models]
        except Exception:
            return []


class OllamaWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        client: OllamaClient,
        prompt: str = "",
        system: Optional[str] = None,
        use_chat: bool = False,
        messages: Optional[List[Dict[str, str]]] = None,
    ):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.system = system
        self.use_chat = use_chat
        self.messages = messages or []

    def run(self) -> None:
        try:
            if self.use_chat:
                response = self.client.chat(self.messages)
            else:
                response = self.client.generate(self.prompt, self.system)
            self.finished.emit(response)
        except Exception as exc:
            self.error.emit(f"Ошибка при генерации: {exc}")
