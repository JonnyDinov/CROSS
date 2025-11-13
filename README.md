# Windows AI Agent

> 🚀 **Быстрый старт:** Смотрите [QUICK_START.md](QUICK_START.md) для немедленного запуска!

Полнофункциональный AI-ассистент для Windows с фоновым сервисом, глобальными горячими клавишами, CLI и современным GUI на PySide6. Агент интегрируется с [Ollama](https://github.com/jmorganca/ollama) для работы с LLM и предоставляет системную автоматизацию, обработку текста и анализ изображений.

---

A full-featured Windows AI assistant with background service, global hotkeys, CLI, and a modern PySide6-based GUI. The agent integrates with [Ollama](https://github.com/jmorganca/ollama) for LLM capabilities and provides deep system automation, text processing, and vision support.

## Features

- **Professional GUI**: modern dark theme inspired by Raycast and VS Code, built with PySide6.
- **Command Palette**: global `Ctrl+P` prompt launcher with templates, categories, and history.
- **Background Agent**: Windows-compatible service with global hotkeys (`Ctrl+P`, `Ctrl+E`) and clipboard integration.
- **System Automation**: folder/file operations, executable launch/termination, notifications, and more.
- **Text Processing**: `Ctrl+E` captures selected text, processes it via Ollama, and updates the clipboard.
- **Vision Support**: capture screen, analyze with vision models (requires compatible Ollama model).
- **CLI**: Rich + Prompt Toolkit experience with history, interactive mode, and streaming responses.
- **Logging**: JSON logs stored under `%LOCALAPPDATA%/WindowsAIAgent/logs`.
- **Build Scripts**: PyInstaller script for producing `agent.exe`.

## Requirements

- Windows 10/11
- Python 3.10+
- Ollama server running at `http://127.0.0.1:11434` with model `gpt-oss:120b-cloud`

## Installation

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Ollama

```bash
ollama pull gpt-oss:120b-cloud
```

## Running

### Run Menu (recommended on Windows)
```
run.bat
```

### GUI
```bash
python -m agent.gui.main
```

### CLI
```bash
agent-cli run "Summarize the latest report"
agent-cli interactive
```

### Background Service
```bash
agent-service
```

### Test Connection (optional)
```bash
python test_connection.py
```

## Build Executables

Ensure PyInstaller is installed (`pip install pyinstaller`).

```bash
python scripts/build.py --target gui    # Build GUI exe
python scripts/build.py --target cli    # Build CLI exe
python scripts/build.py --target all    # Build both
```

Executables are placed in the `dist/` directory.

## Folder Structure

```
agent/
  cli/            # CLI entry points and commands
  core/           # Core agent logic (LLM integration, command execution)
  gui/            # PySide6 GUI
  integrations/   # System integrations (Ollama, Windows APIs)
  services/       # Background services (Hotkeys, agent service)
  utils/          # Utility helpers (async, etc.)
scripts/
  build.py        # PyInstaller builders
resources/        # Icons and assets (add your icons here)
```

## Configuration

Configuration, history, and templates are stored under `%LOCALAPPDATA%/WindowsAIAgent/`:

- `config.yaml`
- `history.json`
- `templates.json`
- `logs/agent.log`

Use the GUI settings panel or edit `config.yaml` directly to customize:

- Ollama models & temperature
- Hotkeys
- Agent update frequency
- Security confirmations
- GUI theme settings

## Security & Permissions

Sensitive operations (process termination, executable launch, file modifications) require confirmation unless disabled in settings. The agent respects allowed/blocked directories configured in `config.yaml`.

## Hotkeys

- `Ctrl+P`: Command palette
- `Ctrl+E`: Process selected text via Ollama

Hotkeys can be customized in settings. The agent uses the `keyboard` library for system-wide hooks and falls back gracefully if unavailable.

## Logging & History

- Logs: JSON records for easy ingestion.
- History: prompts and responses saved for reuse.

Access both in the GUI under the Logs tab.

## Vision Features

Requires a vision-capable model (e.g., `llava`). The "Analyze Screen" button captures the active window and sends it to the vision model for description and analysis.

## License

MIT License
