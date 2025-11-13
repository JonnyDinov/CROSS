from setuptools import setup, find_packages

setup(
    name="windows-ai-agent",
    version="0.1.0",
    description="Windows AI Agent with GUI, CLI, and system automation",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.6.0",
        "keyboard>=0.13.5",
        "pyperclip>=1.8.2",
        "psutil>=5.9.6",
        "requests>=2.31.0",
        "Pillow>=10.1.0",
        "screeninfo>=0.8.1",
        "rich>=13.7.0",
        "prompt-toolkit>=3.0.43",
        "click>=8.1.7",
        "pystray>=0.19.5",
        "plyer>=2.1.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "agent-cli=agent.cli.main:app",
            "agent-service=agent.services.agent_service:run_service",
        ],
        "gui_scripts": [
            "agent-gui=agent.gui.main:run",
        ]
    },
)
