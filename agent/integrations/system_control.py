from __future__ import annotations

import logging
import os
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import pyperclip

try:
    import win32gui
    import win32process
    import win32con
    import win32api
except ImportError:  # pragma: no cover
    win32gui = None
    win32process = None
    win32con = None
    win32api = None


@dataclass
class CommandContext:
    prompt: str
    parameters: Dict[str, Any]
    require_confirmation: bool = False
    user_confirmation: Optional[bool] = None


class SystemController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_folder(self, path: str) -> str:
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return f"Folder created at {path}"
        except Exception as e:
            error_msg = f"Failed to create folder: {e}"
            self.logger.error(error_msg)
            return error_msg

    def move_or_rename(self, src: str, dest: str) -> str:
        try:
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(src).replace(dest)
            return f"Moved/Renamed {src} to {dest}"
        except Exception as e:
            error_msg = f"Failed to move/rename: {e}"
            self.logger.error(error_msg)
            return error_msg

    def launch_executable(self, path: str, args: Optional[str] = None) -> str:
        try:
            cmd = [path]
            if args:
                cmd.extend(args.split())
            subprocess.Popen(cmd, shell=True)
            return f"Launched {path}"
        except Exception as e:
            error_msg = f"Failed to launch executable: {e}"
            self.logger.error(error_msg)
            return error_msg

    def terminate_process(self, name: str) -> str:
        try:
            if os.name != "nt":
                return "Process termination is only supported on Windows."

            taskkill = ["taskkill", "/IM", name, "/F"]
            subprocess.check_call(taskkill, shell=True)
            return f"Terminated {name}"
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to terminate process: {e}"
            self.logger.error(error_msg)
            return error_msg

    def open_website(self, url: str) -> str:
        try:
            webbrowser.open(url)
            return f"Opened {url}"
        except Exception as e:
            error_msg = f"Failed to open website: {e}"
            self.logger.error(error_msg)
            return error_msg

    def close_application(self, window_title: str) -> str:
        if win32gui is None:
            return "Windows APIs not available."
        
        try:
            def enum_handler(hwnd, _):
                if window_title.lower() in win32gui.GetWindowText(hwnd).lower():
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            win32gui.EnumWindows(enum_handler, None)
            return f"Close signal sent to {window_title}"
        except Exception as e:
            error_msg = f"Failed to close application: {e}"
            self.logger.error(error_msg)
            return error_msg

    def read_clipboard(self) -> str:
        try:
            return pyperclip.paste() or ""
        except Exception as e:
            error_msg = f"Failed to read clipboard: {e}"
            self.logger.error(error_msg)
            return error_msg

    def write_clipboard(self, text: str) -> str:
        try:
            pyperclip.copy(text)
            return "Clipboard updated"
        except Exception as e:
            error_msg = f"Failed to write clipboard: {e}"
            self.logger.error(error_msg)
            return error_msg

    def modify_text_file(self, path: str, content: str) -> str:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File {path} updated"
        except Exception as e:
            error_msg = f"Failed to modify text file: {e}"
            self.logger.error(error_msg)
            return error_msg

    def read_active_window(self) -> str:
        if win32gui is None:
            return "Windows APIs not available."
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            length = win32gui.GetWindowTextLength(hwnd)
            return win32gui.GetWindowText(hwnd)[:length]
        except Exception as e:
            error_msg = f"Failed to read active window: {e}"
            self.logger.error(error_msg)
            return error_msg

    def send_system_notification(self, title: str, message: str) -> str:
        try:
            if os.name == "nt":
                from plyer import notification
                notification.notify(title=title, message=message, app_name="AI Agent")
            else:
                self.logger.info("Notifications are not supported on this platform in demo mode.")
            return "Notification sent"
        except Exception as e:
            error_msg = f"Failed to send notification: {e}"
            self.logger.error(error_msg)
            return error_msg

    def capture_active_window(self, output_path: str) -> str:
        try:
            from PIL import ImageGrab
            image = ImageGrab.grab()
            image.save(output_path)
            return f"Screenshot saved to {output_path}"
        except Exception as e:
            error_msg = f"Failed to capture screenshot: {e}"
            self.logger.error(error_msg)
            return error_msg


system_controller = SystemController()
