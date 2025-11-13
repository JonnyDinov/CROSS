from __future__ import annotations

import logging
from typing import Optional, Generator, Dict, Any, List
import requests
import json

from agent.config import config


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.base_url = base_url or config.get("ollama.base_url", "http://localhost:11434")
        self.model = model or config.get("ollama.model", "llama3.2:latest")
        self.vision_model = config.get("ollama.vision_model", "llava:latest")
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Ollama is not available: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            return []
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        model = model or self.model

        messages: List[Dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            stream=stream
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout if not stream else None,
                stream=stream
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code}"
                self.logger.error(error_msg)
                return error_msg if not stream else iter([error_msg])

            if stream:
                return self._stream_chat_response(response)
            else:
                result = response.json()
                return result.get("message", {}).get("content", "")
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out"
            self.logger.error(error_msg)
            return error_msg if not stream else iter([error_msg])
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            self.logger.error(error_msg)
            return error_msg if not stream else iter([error_msg])

    def _stream_chat_response(self, response: requests.Response) -> Generator[str, None, None]:
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data:
                            content = data["message"].get("content", "")
                            if content:
                                yield content
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Error streaming response: {e}")
            yield f"Error: {str(e)}"

    def generate_with_image(
        self,
        prompt: str,
        image_path: str,
        model: Optional[str] = None
    ) -> str:
        import base64
        
        model = model or self.vision_model
        
        try:
            with open(image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")
        except Exception as e:
            error_msg = f"Failed to read image: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [img_data],
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code}"
                self.logger.error(error_msg)
                return error_msg

            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            self.logger.error(error_msg)
            return error_msg


ollama_client = OllamaClient()
