import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

APP_NAME = "WindowsAIAgent"
APP_DIR = Path(os.getenv("LOCALAPPDATA", ".")) / APP_NAME
CONFIG_FILE = APP_DIR / "config.yaml"
LOGS_DIR = APP_DIR / "logs"
HISTORY_FILE = APP_DIR / "history.json"
TEMPLATES_FILE = APP_DIR / "templates.json"

APP_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class Config:
    DEFAULT_CONFIG = {
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "llama3.2:latest",
            "vision_model": "llava:latest",
            "timeout": 120,
            "temperature": 0.7,
        },
        "hotkeys": {
            "prompt_panel": "ctrl+p",
            "text_processing": "ctrl+e",
        },
        "gui": {
            "theme": "dark",
            "opacity": 0.95,
            "font_size": 12,
            "animation_duration": 200,
            "window_width": 800,
            "window_height": 600,
        },
        "agent": {
            "update_frequency": 1.0,
            "max_history": 100,
            "log_level": "INFO",
            "auto_start": False,
        },
        "security": {
            "require_confirmation_for_delete": True,
            "require_confirmation_for_execute": True,
            "allowed_directories": [],
            "blocked_directories": ["C:\\Windows\\System32"],
        },
    }

    def __init__(self):
        self.config: Dict[str, Any] = self.load()

    def load(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    return self._merge_configs(self.DEFAULT_CONFIG.copy(), config or {})
            except Exception as e:
                print(f"Failed to load config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.save(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save(self, config: Optional[Dict[str, Any]] = None):
        if config is not None:
            self.config = config
        
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any):
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()


class HistoryManager:
    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.history = self.load()

    def load(self) -> list:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history[-self.max_items:], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save history: {e}")

    def add(self, item: Dict[str, Any]):
        self.history.append(item)
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items:]
        self.save()

    def clear(self):
        self.history = []
        self.save()

    def search(self, query: str) -> list:
        query = query.lower()
        return [
            item for item in self.history
            if query in item.get("prompt", "").lower()
            or query in item.get("response", "").lower()
        ]


class TemplateManager:
    DEFAULT_TEMPLATES = [
        {
            "id": "translate",
            "name": "Translate Text",
            "prompt": "Translate the following text to English:\n{text}",
            "category": "Text Processing",
            "icon": "🌐",
        },
        {
            "id": "summarize",
            "name": "Summarize",
            "prompt": "Summarize the following text concisely:\n{text}",
            "category": "Text Processing",
            "icon": "📝",
        },
        {
            "id": "fix_grammar",
            "name": "Fix Grammar",
            "prompt": "Fix grammar and spelling in the following text:\n{text}",
            "category": "Text Processing",
            "icon": "✍️",
        },
        {
            "id": "create_folder",
            "name": "Create Folder",
            "prompt": "Create a folder at: {path}",
            "category": "System",
            "icon": "📁",
        },
        {
            "id": "open_website",
            "name": "Open Website",
            "prompt": "Open {url} in browser",
            "category": "System",
            "icon": "🌐",
        },
    ]

    def __init__(self):
        self.templates = self.load()

    def load(self) -> list:
        if TEMPLATES_FILE.exists():
            try:
                with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                self.save(self.DEFAULT_TEMPLATES)
                return self.DEFAULT_TEMPLATES.copy()
        else:
            self.save(self.DEFAULT_TEMPLATES)
            return self.DEFAULT_TEMPLATES.copy()

    def save(self, templates: Optional[list] = None):
        if templates is not None:
            self.templates = templates
        
        try:
            with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save templates: {e}")

    def get_by_category(self, category: str) -> list:
        return [t for t in self.templates if t.get("category") == category]

    def get_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        for t in self.templates:
            if t.get("id") == template_id:
                return t
        return None

    def add_template(self, template: Dict[str, Any]):
        self.templates.append(template)
        self.save()

    def remove_template(self, template_id: str):
        self.templates = [t for t in self.templates if t.get("id") != template_id]
        self.save()


config = Config()
history_manager = HistoryManager()
template_manager = TemplateManager()
