# Architecture Documentation

## Overview

Windows AI Agent is a desktop application that provides AI-powered system automation, text processing, and screen analysis capabilities. The application is built with Python using PySide6 for the GUI and integrates with Ollama for LLM functionality.

## Core Components

### 1. Agent Core (`agent/core/`)

**agent.py**
- Main AI agent implementation
- Integrates with Ollama for LLM inference
- Command execution and action dispatch
- History management

**logging.py**
- JSON-based logging system
- Configurable log levels
- Structured log output for easy parsing

### 2. GUI Layer (`agent/gui/`)

Built with PySide6 (Qt for Python 6), following modern design patterns.

**main.py**
- Application entry point
- Qt application initialization

**styles.py**
- Dark theme stylesheet
- Consistent UI styling across components
- Inspired by VS Code / Raycast aesthetics

**views/**
- `main_window.py`: Main application window with tab-based layout
- `prompt_panel.py`: Command palette with templates and history
- `settings_panel.py`: Configuration interface
- `log_panel.py`: JSON log viewer with filtering

**Features:**
- Drag-and-drop file support
- System tray integration
- Global hotkey registration
- Confirmation dialogs for dangerous operations

### 3. CLI Layer (`agent/cli/`)

**main.py**
- Click-based command-line interface
- Rich terminal output with markdown rendering
- Interactive mode with prompt-toolkit
- History and info commands

**Commands:**
- `run`: Execute single prompt
- `interactive`: Enter interactive mode
- `gui`: Launch GUI from CLI
- `info`: System and model information
- `history`: View command history
- `clear-history`: Clear command history

### 4. Integrations (`agent/integrations/`)

**ollama_client.py**
- HTTP client for Ollama API
- Streaming and non-streaming responses
- Chat and generation endpoints
- Vision model support

**system_control.py**
- Windows system operations
- File/folder management
- Process control (launch, terminate)
- Clipboard integration
- Screen capture
- System notifications

### 5. Services (`agent/services/`)

**hotkeys.py**
- Global hotkey registration using `keyboard` library
- Thread-safe hotkey management
- Configurable key combinations

**agent_service.py**
- Background service implementation
- Continuous operation mode
- Integration with hotkey service

### 6. Configuration (`agent/config.py`)

Centralized configuration management:
- YAML-based config file
- Default configuration values
- Config path: `%LOCALAPPDATA%/WindowsAIAgent/config.yaml`

**Config Sections:**
- `ollama`: API settings, model selection
- `hotkeys`: Key combination mappings
- `gui`: Theme and UI settings
- `agent`: Update frequency, logging
- `security`: Operation confirmations, directory restrictions

**History Manager:**
- JSON-based history storage
- Prompt/response pairs
- Timestamp tracking
- Search functionality

**Template Manager:**
- Pre-defined prompt templates
- Category organization
- Custom template support

## Data Flow

### Prompt Processing Flow

```
User Input (GUI/CLI)
    ↓
Agent.process_prompt()
    ↓
Ollama API Request
    ↓
Response (streaming or complete)
    ↓
Action Extraction (JSON parsing)
    ↓
Action Dispatch
    ↓
System Controller Execution
    ↓
History Storage
    ↓
Response to User
```

### Hotkey Flow

```
User Presses Hotkey
    ↓
Hotkey Service (keyboard library)
    ↓
Signal Emission
    ↓
Main Window Handler
    ↓
Show Prompt Panel / Process Text
```

## Security Model

### Confirmation Requirements

Dangerous actions require user confirmation:
- Process termination
- Executable launch
- File modifications

Configuration setting: `security.require_confirmation_for_execute`

### Directory Restrictions

- Allowed directories list
- Blocked directories (e.g., System32)
- Configurable in `config.yaml`

## Build System

### PyInstaller Configuration

Located in `scripts/build.py`

**GUI Build:**
- Windowed mode (no console)
- PySide6 bundling
- Icon support
- Single executable output

**CLI Build:**
- Console mode
- Rich/Click bundling
- Single executable output

**Service Build:**
- Console mode for service logging
- Minimal dependencies

**Build Commands:**
```bash
python scripts/build.py --target gui
python scripts/build.py --target cli
python scripts/build.py --target service
python scripts/build.py --target all
```

## Deployment

### Directory Structure

```
%LOCALAPPDATA%/WindowsAIAgent/
  ├── config.yaml
  ├── history.json
  ├── templates.json
  └── logs/
      └── agent.log
```

### Dependencies

**Core:**
- PySide6: GUI framework
- Click: CLI framework
- Rich: Terminal output
- Requests: HTTP client
- PyYAML: Configuration parsing

**System Integration:**
- keyboard: Global hotkeys
- pyperclip: Clipboard access
- pywin32: Windows APIs (optional)
- pystray: System tray
- Pillow: Screen capture
- plyer: Notifications

## Extension Points

### Adding New Actions

1. Add action handler to `SystemController`
2. Update `AIAgent._dispatch_action()` mapping
3. Document in system prompt

### Adding New Templates

1. Edit `templates.json` or use GUI
2. Define prompt with placeholders
3. Assign category and icon

### Custom Models

Configure in `config.yaml`:
```yaml
ollama:
  model: "your-model:latest"
  vision_model: "your-vision-model:latest"
```

## Performance Considerations

- Streaming responses for long-running queries
- Thread-based hotkey listener (non-blocking)
- Background service mode for minimal resource usage
- JSON logs for efficient parsing

## Future Enhancements

- Multi-language support
- Plugin system
- Custom action scripts
- Voice input integration
- Cloud sync for history/templates
- Advanced screen analysis with OCR
- Windows Task Scheduler integration
