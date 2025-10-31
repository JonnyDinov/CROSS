import json
from typing import List, Optional, Dict, Any, Callable
import requests


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = 0.7
        self.top_p = 0.9

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {"temperature": self.temperature, "top_p": self.top_p},
        }
        if system:
            payload["system"] = system

        if stream and callback:
            response = requests.post(url, json=payload, stream=True, timeout=300)
            response.raise_for_status()

            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        text = chunk["response"]
                        full_text += text
                        callback(text)
            return full_text
        else:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    def chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": self.temperature, "top_p": self.top_p},
        }

        if stream and callback:
            response = requests.post(url, json=payload, stream=True, timeout=300)
            response.raise_for_status()

            full_text = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "message" in chunk and "content" in chunk["message"]:
                        text = chunk["message"]["content"]
                        full_text += text
                        callback(text)
            return full_text
        else:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    def embed_text(self, text: str) -> Optional[List[float]]:
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": text}

        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("embedding")
        except Exception:
            return None

    def test_connection(self) -> bool:
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []
