from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
)

from agent.config import LOGS_DIR


class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._build_ui()
        self._load_logs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Action Log")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        controls = QHBoxLayout()

        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "INFO", "WARNING", "ERROR", "DEBUG"])
        self.level_filter.currentTextChanged.connect(self._load_logs)
        controls.addWidget(self.level_filter)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("SecondaryButton")
        self.refresh_button.clicked.connect(self._load_logs)
        controls.addWidget(self.refresh_button)

        controls.addStretch()
        layout.addLayout(controls)

        self.log_list = QListWidget()
        self.log_list.itemSelectionChanged.connect(self._display_selected_log)
        layout.addWidget(self.log_list)

        self.log_details = QTextEdit()
        self.log_details.setReadOnly(True)
        self.log_details.setPlaceholderText("Select a log entry to see details")
        layout.addWidget(self.log_details)

    def _load_logs(self):
        self.log_list.clear()
        level_filter = self.level_filter.currentText()

        log_file = LOGS_DIR / "agent.log"
        if not log_file.exists():
            return

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        level = entry.get("level", "INFO")
                        if level_filter != "ALL" and level != level_filter:
                            continue
                        item = QListWidgetItem(f"{entry['timestamp']} [{level}] {entry.get('message', '')}")
                        item.setData(Qt.ItemDataRole.UserRole, entry)
                        self.log_list.addItem(item)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to load logs: {e}")

    def _display_selected_log(self):
        selected = self.log_list.currentItem()
        if not selected:
            self.log_details.clear()
            return

        entry = selected.data(Qt.ItemDataRole.UserRole)
        if entry:
            formatted = json.dumps(entry, indent=2, ensure_ascii=False)
            self.log_details.setPlainText(formatted)
