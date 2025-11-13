import os
import sys
import subprocess
from pathlib import Path

DATA_SEP = ";" if os.name == "nt" else ":"


def build_gui_exe():
    print("=" * 50)
    print("Building GUI Executable")
    print("=" * 50)

    base_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "WindowsAIAgent",
        "--onefile",
        "--windowed",
        "--hidden-import",
        "PySide6",
        "--hidden-import",
        "agent",
        "--hidden-import",
        "agent.gui",
        "--hidden-import",
        "agent.core",
        "--hidden-import",
        "agent.integrations",
        "--hidden-import",
        "agent.services",
        "--collect-all",
        "PySide6",
        "--add-data",
        f"agent{DATA_SEP}agent",
    ]

    icon_path = Path("resources/icon.ico")
    if icon_path.exists():
        base_cmd.extend(["--icon", str(icon_path)])

    base_cmd.append("agent/gui_app.py")

    subprocess.check_call(base_cmd)


def build_cli_exe():
    print("=" * 50)
    print("Building CLI Executable")
    print("=" * 50)

    base_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "agent-cli",
        "--onefile",
        "--console",
        "--hidden-import",
        "click",
        "--hidden-import",
        "rich",
        "--hidden-import",
        "agent",
        "--hidden-import",
        "agent.cli",
        "--hidden-import",
        "agent.core",
        "--hidden-import",
        "agent.integrations",
        "--hidden-import",
        "agent.services",
        "--add-data",
        f"agent{DATA_SEP}agent",
        "agent/cli_app.py",
    ]

    subprocess.check_call(base_cmd)


def build_service_exe():
    print("=" * 50)
    print("Building Service Executable")
    print("=" * 50)

    base_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "agent-service",
        "--onefile",
        "--console",
        "--hidden-import",
        "agent",
        "--hidden-import",
        "agent.services",
        "--add-data",
        f"agent{DATA_SEP}agent",
        "agent/service_app.py",
    ]

    subprocess.check_call(base_cmd)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Windows AI Agent executables")
    parser.add_argument("--target", choices=["gui", "cli", "service", "all"], default="all", help="Build target")

    args = parser.parse_args()

    if args.target in ("gui", "all"):
        build_gui_exe()

    if args.target in ("cli", "all"):
        build_cli_exe()

    if args.target in ("service", "all"):
        build_service_exe()

    print("\n" + "=" * 50)
    print("Build Complete!")
    print("Check the 'dist' folder for executables")
    print("=" * 50)
