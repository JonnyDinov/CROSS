from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from typing import Optional, Callable, Dict, Any

from agent.config import config, history_manager
from agent.integrations.ollama_client import ollama_client
from agent.integrations.system_control import system_controller


class AIAgent:
    SYSTEM_PROMPT = """You are an AI assistant that helps users control their Windows system and process text.

You can execute the following commands by responding with JSON:

1. Create folder: {"action": "create_folder", "path": "C:/path/to/folder"}
2. Move/rename file: {"action": "move_or_rename", "src": "C:/old.txt", "dest": "C:/new.txt"}
3. Launch executable: {"action": "launch_executable", "path": "C:/app.exe", "args": "optional args"}
4. Terminate process: {"action": "terminate_process", "name": "notepad.exe"}
5. Open website: {"action": "open_website", "url": "https://example.com"}
6. Close application: {"action": "close_application", "window_title": "Notepad"}
7. Read clipboard: {"action": "read_clipboard"}
8. Write clipboard: {"action": "write_clipboard", "text": "content"}
9. Modify file: {"action": "modify_text_file", "path": "C:/file.txt", "content": "new content"}
10. Capture screenshot: {"action": "capture_screenshot", "path": "C:/screenshot.png"}
11. Send notification: {"action": "send_notification", "title": "Title", "message": "Message"}

For text processing, just respond with the processed text.
If unsure, respond with a helpful message or ask for clarification.
"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ollama = ollama_client
        self.system = system_controller
        self.confirmation_callback: Optional[Callable[[str], bool]] = None

    def set_confirmation_callback(self, callback: Callable[[str], bool]):
        self.confirmation_callback = callback

    def process_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        stream: bool = False,
        callback: Optional[Callable[[str], None]] = None
    ) -> str:
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"

            self.logger.info(f"Processing prompt: {prompt}")

            if stream:
                response_parts = []
                for chunk in self.ollama.generate(
                    full_prompt,
                    system=self.SYSTEM_PROMPT,
                    stream=True
                ):
                    response_parts.append(chunk)
                    if callback:
                        callback(chunk)
                response = "".join(response_parts)
            else:
                response = self.ollama.generate(
                    full_prompt,
                    system=self.SYSTEM_PROMPT,
                    stream=False
                )

            self._add_to_history(prompt, response)

            action_result = self._execute_action(response)
            if action_result:
                return action_result

            return response

        except Exception as e:
            error_msg = f"Error processing prompt: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def process_text(self, text: str, instruction: str) -> str:
        prompt = f"{instruction}\n\nText:\n{text}"
        return self.process_prompt(prompt)

    def analyze_image(self, image_path: str, prompt: str) -> str:
        try:
            self.logger.info(f"Analyzing image: {image_path}")
            response = self.ollama.generate_with_image(prompt, image_path)
            self._add_to_history(f"[Image: {image_path}] {prompt}", response)
            return response
        except Exception as e:
            error_msg = f"Error analyzing image: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def _execute_action(self, response: str) -> Optional[str]:
        try:
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response)
            if not json_match:
                return None

            action_data = json.loads(json_match.group())
            action = action_data.get("action")

            if not action:
                return None

            self.logger.info(f"Executing action: {action}")

            if self._requires_confirmation(action):
                if self.confirmation_callback:
                    confirmed = self.confirmation_callback(
                        f"Execute action: {action}\nParameters: {action_data}"
                    )
                    if not confirmed:
                        return "Action cancelled by user."
                else:
                    self.logger.warning("Confirmation required but no callback set.")
                    return "Action requires confirmation but no callback available."

            result = self._dispatch_action(action, action_data)
            return result

        except json.JSONDecodeError:
            return None
        except Exception as e:
            error_msg = f"Error executing action: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def _requires_confirmation(self, action: str) -> bool:
        dangerous_actions = [
            "terminate_process",
            "launch_executable",
            "modify_text_file",
        ]
        return action in dangerous_actions and config.get(
            "security.require_confirmation_for_execute", True
        )

    def _dispatch_action(self, action: str, data: Dict[str, Any]) -> str:
        action_map = {
            "create_folder": lambda: self.system.create_folder(data["path"]),
            "move_or_rename": lambda: self.system.move_or_rename(data["src"], data["dest"]),
            "launch_executable": lambda: self.system.launch_executable(
                data["path"], data.get("args")
            ),
            "terminate_process": lambda: self.system.terminate_process(data["name"]),
            "open_website": lambda: self.system.open_website(data["url"]),
            "close_application": lambda: self.system.close_application(data["window_title"]),
            "read_clipboard": lambda: self.system.read_clipboard(),
            "write_clipboard": lambda: self.system.write_clipboard(data["text"]),
            "modify_text_file": lambda: self.system.modify_text_file(
                data["path"], data["content"]
            ),
            "capture_screenshot": lambda: self.system.capture_active_window(data["path"]),
            "send_notification": lambda: self.system.send_system_notification(
                data["title"], data["message"]
            ),
        }

        handler = action_map.get(action)
        if handler:
            return handler()
        else:
            return f"Unknown action: {action}"

    def _add_to_history(self, prompt: str, response: str):
        history_manager.add({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
        })


agent = AIAgent()
