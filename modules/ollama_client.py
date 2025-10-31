import requests
from typing import Optional, Dict, List, Any
from PyQt5.QtCore import QThread, pyqtSignal


class OllamaClient:
    def __init__(self, api_url: str = "http://localhost:11434", model: str = "llama2"):
        self.api_url = api_url.rstrip("/")
        self.model = model
        self._chat_available: Optional[bool] = None
        self._connection_checked = False

    def _check_connection(self) -> None:
        """Проверка доступности Ollama"""
        if self._connection_checked:
            return
        try:
            requests.get(f"{self.api_url}/", timeout=5)
            self._connection_checked = True
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Ollama недоступна по адресу {self.api_url}\n"
                "Убедитесь, что Ollama запущена (команда: ollama serve)"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка подключения к Ollama: {e}")

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Генерация текста через /api/generate"""
        self._check_connection()
        
        url = f"{self.api_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        try:
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
            
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else ""
            if status == 404:
                raise RuntimeError(
                    f"Модель '{self.model}' не найдена.\n"
                    f"Загрузите модель: ollama pull {self.model}"
                )
            raise RuntimeError(f"HTTP ошибка: {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к Ollama: {e}")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Генерация через /api/chat или fallback на /api/generate"""
        self._check_connection()
        
        # Сначала пробуем Chat API
        if self._chat_available is not False:
            try:
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
                    text = data.get("response")
                if not text:
                    raise RuntimeError("Пустой ответ от Ollama")
                
                self._chat_available = True
                return text
                
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else ""
                if status == 404:
                    # Chat API недоступен, используем generate
                    self._chat_available = False
                else:
                    raise RuntimeError(f"HTTP ошибка: {e}")
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Ошибка запроса к Ollama: {e}")
        
        # Fallback: используем generate API
        system_msg = None
        user_msgs = []
        
        for msg in messages:
            if msg.get("role") == "system" and system_msg is None:
                system_msg = msg.get("content", "")
            elif msg.get("role") in ["user", "assistant"]:
                role = "Пользователь" if msg["role"] == "user" else "Ассистент"
                user_msgs.append(f"{role}: {msg.get('content', '')}")
        
        prompt_lines = user_msgs + ["Ассистент:"]
        prompt = "\n".join(prompt_lines)
        return self.generate(prompt, system_msg)

    def get_available_models(self) -> List[str]:
        try:
            url = f"{self.api_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            models = result.get("models", [])
            return [model["name"] for model in models]
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Не удалось подключиться к Ollama по адресу {self.api_url}."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка при получении списка моделей: {e}")


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
