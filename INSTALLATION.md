# Installation Guide

## System Requirements

- Operating System: Windows 10/11
- Python: 3.9 or higher
- Ollama: Latest version running on `http://localhost:11434`

## Step 1: Install Python

Download Python from https://python.org and install with "Add to PATH" option enabled.

Verify installation:
```bash
python --version
```

## Step 2: Install Ollama

Download Ollama from https://ollama.ai and install.

Start Ollama service and pull required model:

```bash
ollama serve
ollama pull gpt-oss:120b-cloud
```

## Step 3: Clone/Download Repository

```bash
git clone <repository-url>
cd windows-ai-agent
```

## Step 4: Create Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

If using Windows-specific features (highly recommended):
```bash
pip install pywin32
```

## Step 6: Run the Application

### Quick Menu (Windows)
```
run.bat
```

### GUI Mode
```bash
python -m agent.gui.main
```

Or:
```bash
python agent/gui_app.py
```

### CLI Mode
```bash
python -m agent.cli.main run "Open YouTube"
```

Or interactive:
```bash
python -m agent.cli.main interactive
```

### Background Service
```bash
python -m agent.services.agent_service
```

## Step 7: Build Executables (Optional)

To create standalone `.exe` files:

```bash
pip install pyinstaller
python scripts/build.py --target all
```

Executables will be in `dist/` folder.

## Configuration

First run creates configuration at: `%LOCALAPPDATA%\WindowsAIAgent\config.yaml`

Edit settings via:
- GUI: Settings tab
- Manual: edit `config.yaml`

## Troubleshooting

### Ollama Connection Error

Make sure Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### Hotkeys Not Working

- Run as Administrator
- Check if another app uses the same hotkeys
- Disable in Settings and re-enable

### GUI Won't Start

Check dependencies:
```bash
pip list | grep PySide6
```

Reinstall if needed:
```bash
pip install --upgrade PySide6
```

### Permission Errors

Some system operations require Administrator privileges.

## Next Steps

1. Configure your preferred Ollama model in Settings
2. Customize hotkeys (default: `Ctrl+P`, `Ctrl+E`)
3. Try sample commands:
   - "Create a folder on Desktop called Test"
   - "Open YouTube"
   - "Summarize this text: [paste text]"
4. Set up auto-start (Settings → Agent Settings → Start with Windows)

## Support

For issues, please check:
- Logs: `%LOCALAPPDATA%\WindowsAIAgent\logs\agent.log`
- Configuration: `%LOCALAPPDATA%\WindowsAIAgent\config.yaml`
