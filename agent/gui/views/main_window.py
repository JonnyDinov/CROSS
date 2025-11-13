from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QTabWidget,
    QMessageBox,
)

from agent.config import config
from agent.gui.styles import DARK_THEME
from agent.gui.views.prompt_panel import PromptPanel
from agent.gui.views.settings_panel import SettingsPanel
from agent.gui.views.log_panel import LogPanel
from agent.services.hotkeys import hotkey_service

if TYPE_CHECKING:
    from agent.core.agent import AIAgent


class MainWindow(QMainWindow):
    show_prompt_signal = Signal()
    show_text_processing_signal = Signal()

    def __init__(self, ai_agent: AIAgent):
        super().__init__()
        self.agent = ai_agent
        self.logger = logging.getLogger(__name__)
        
        self.agent.set_confirmation_callback(self._confirm_action)
        
        self.setWindowTitle("Windows AI Agent")
        self.setMinimumSize(800, 600)
        self.resize(
            config.get("gui.window_width", 800),
            config.get("gui.window_height", 600)
        )

        self._setup_ui()
        self._setup_tray_icon()
        self._setup_hotkeys()
        self._apply_theme()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        
        self.prompt_panel = PromptPanel(self.agent)
        self.settings_panel = SettingsPanel()
        self.log_panel = LogPanel()

        self.tab_widget.addTab(self.prompt_panel, "🎯 Prompt")
        self.tab_widget.addTab(self.log_panel, "📋 Logs")
        self.tab_widget.addTab(self.settings_panel, "⚙️ Settings")

        layout.addWidget(self.tab_widget)

        self._setup_menu_bar()

        self.statusBar().showMessage("AI Agent Ready")

    def _setup_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        
        show_action = QAction("&Show", self)
        show_action.triggered.connect(self.show_window)
        file_menu.addAction(show_action)

        hide_action = QAction("&Hide", self)
        hide_action.triggered.connect(self.hide)
        file_menu.addAction(hide_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.quit_app)
        file_menu.addAction(quit_action)

        view_menu = menu_bar.addMenu("&View")
        
        prompt_action = QAction("Show &Prompt Panel", self)
        prompt_action.setShortcut(QKeySequence("Ctrl+P"))
        prompt_action.triggered.connect(self.show_prompt_panel)
        view_menu.addAction(prompt_action)

    def _setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Windows AI Agent")

        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def _setup_hotkeys(self):
        self.show_prompt_signal.connect(self.show_prompt_panel)
        self.show_text_processing_signal.connect(self._handle_text_processing)

        hotkey_service.load_from_config(
            lambda: self.show_prompt_signal.emit(),
            lambda: self.show_text_processing_signal.emit()
        )
        hotkey_service.start()

    def _apply_theme(self):
        self.setStyleSheet(DARK_THEME)

    def _confirm_action(self, message: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Confirm Action")
        dialog.setText(message)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        result = dialog.exec()
        return result == QMessageBox.StandardButton.Yes

    def show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def show_prompt_panel(self):
        self.show_window()
        self.tab_widget.setCurrentWidget(self.prompt_panel)
        self.prompt_panel.focus_input()

    def _handle_text_processing(self):
        self.logger.info("Text processing hotkey triggered")
        
        try:
            import pyperclip
            selected_text = pyperclip.paste()
            
            if selected_text:
                self.show_window()
                self.tab_widget.setCurrentWidget(self.prompt_panel)
                self.prompt_panel.set_context_text(selected_text)
                self.prompt_panel.focus_input()
            else:
                self.statusBar().showMessage("No text in clipboard", 3000)
        except Exception as e:
            self.logger.error(f"Failed to process text: {e}")

    def quit_app(self):
        hotkey_service.stop()
        self.tray_icon.hide()
        self.close()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Windows AI Agent",
            "Application minimized to tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
