# Usage Examples

## GUI Mode Examples

### Using the Command Palette (Ctrl+P)

1. **Text Translation**
   - Select template: "Translate Text"
   - In Context field: paste your text
   - In Prompt: "Translate to Spanish"
   - Click "Run Prompt"

2. **Analyze Screen**
   - Click "Analyze Screen" button
   - The agent captures the current window
   - Sends it to vision model (requires `llava` or similar)
   - Displays analysis in response area

3. **Custom System Command**
   - In Prompt field: "Create a folder on Desktop called ProjectX"
   - Click "Run Prompt"
   - Agent interprets and creates the folder

### Text Processing (Ctrl+E)

1. Select text anywhere in Windows
2. Press `Ctrl+E`
3. GUI appears with selected text in Context
4. Enter instruction (e.g., "Summarize this")
5. Run and see result

## CLI Mode Examples

### Basic Command Execution

```bash
# Open a website
agent-cli run "Open YouTube"

# Create a folder
agent-cli run "Create a folder at C:\Users\YourName\Desktop\TestFolder"

# Terminate a process
agent-cli run "Close notepad"

# Text processing
agent-cli run "Translate this to French: Hello, how are you?"
```

### Interactive Mode

```bash
agent-cli interactive
```

Then:
```
Prompt: Summarize the following text: [your text]
Prompt: Open Visual Studio Code
Prompt: exit
```

### Streaming Responses

```bash
agent-cli run --stream "Tell me a story about AI"
```

### With Context

```bash
agent-cli run --context "User is working on a Python project" "Create a README file"
```

### System Info

```bash
agent-cli info
agent-cli info --model llama3.2:latest
```

### History Management

```bash
# View history
agent-cli history

# Clear history
agent-cli clear-history
```

## Background Service Examples

Run the service in the background:

```bash
agent-service
```

Or run it as a Windows Service (requires `pywin32` and admin rights):

1. Install service: `sc create AIAgent binPath="C:\path\to\agent-service.exe"`
2. Start service: `sc start AIAgent`

## System Automation Examples

### File & Folder Operations

```bash
agent-cli run "Create folders: C:\Projects\AI and C:\Projects\Data"
agent-cli run "Move C:\test.txt to C:\backup\test.txt"
agent-cli run "Rename C:\oldname.txt to newname.txt"
```

### Process Management

```bash
agent-cli run "Launch C:\Program Files\MyApp\app.exe"
agent-cli run "Terminate process chrome.exe"
agent-cli run "Close the Calculator app"
```

### Web & Notifications

```bash
agent-cli run "Open https://github.com"
agent-cli run "Send notification: Meeting starts in 5 minutes"
```

### Clipboard Integration

```bash
# Read clipboard
agent-cli run "What's in my clipboard?"

# Process and update clipboard
agent-cli run "Translate clipboard content to German"
```

### Vision & Screen Analysis

```bash
# Take screenshot and analyze
agent-cli run "Capture screen and describe what you see"
agent-cli run "Analyze the current window and suggest improvements"
```

## Advanced Use Cases

### Multi-Step Automation

```bash
agent-cli run "Create a project folder on Desktop, then create README.md inside with project description"
```

### Data Collection & Reporting

```bash
agent-cli run "Read files in C:\Reports, summarize each, and create a master report"
```

### Code Assistance

```bash
agent-cli run --context "Python function code here" "Review this code and suggest improvements"
```

### Natural Language Task Planning

```bash
agent-cli run "I need to organize my Desktop. Suggest a folder structure and create it."
```

## Templates & Custom Prompts

In the GUI, you can create custom templates:

1. Go to Prompt Panel
2. Create a new template with placeholders like `{text}`, `{path}`, etc.
3. Save it to `%LOCALAPPDATA%\WindowsAIAgent\templates.json`

Example template:
```json
{
  "id": "code_review",
  "name": "Code Review",
  "prompt": "Review the following code and provide feedback:\n{code}",
  "category": "Development",
  "icon": "💻"
}
```

## Security Notes

- Dangerous operations (process termination, file deletion) require confirmation by default.
- Configure allowed/blocked directories in `config.yaml`.
- Run with appropriate permissions based on your needs.

## Tips

- Use streaming mode for long responses
- Check `agent.log` for troubleshooting
- Customize hotkeys to avoid conflicts
- Use templates for repetitive tasks
- Vision features require appropriate models (e.g., `llava`)
