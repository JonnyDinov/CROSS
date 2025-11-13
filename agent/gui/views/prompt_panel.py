from __future__ import annotations

import logging
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QSplitter,
)

from agent.config import template_manager, history_manager


class PromptListItem(QListWidgetItem):
    def __init__(self, template: Dict[str, str]):
        super().__init__(f"{template.get('icon', '🧠')}  {template['name']}")
        self.template = template


class PromptPanel(QWidget):
    def __init__(self, agent):
        super().__init__()
        self.setObjectName("PromptPanel")
        self.setAcceptDrops(True)
        self.agent = agent
        self.logger = logging.getLogger(__name__)
        
        self._build_ui()
        self._populate_prompts()
        self._populate_history()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Command Palette")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search prompts, categories, history...")
        self.search_input.textChanged.connect(self._filter_prompts)
        layout.addWidget(self.search_input)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        self.prompt_list = QListWidget()
        self.prompt_list.currentItemChanged.connect(self._on_prompt_selected)
        splitter.addWidget(self.prompt_list)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)

        self.template_label = QLabel("Select a prompt template or write custom prompt")
        self.template_label.setObjectName("SubHeaderLabel")
        right_layout.addWidget(self.template_label)

        self.context_input = QTextEdit()
        self.context_input.setPlaceholderText("Optional context (selected text)")
        right_layout.addWidget(self.context_input)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Prompt")
        self.prompt_input.setMinimumHeight(160)
        right_layout.addWidget(self.prompt_input)

        button_row = QHBoxLayout()

        self.run_button = QPushButton("Run Prompt")
        self.run_button.clicked.connect(self._run_prompt)
        button_row.addWidget(self.run_button)

        self.analyze_screen_button = QPushButton("Analyze Screen")
        self.analyze_screen_button.clicked.connect(self._analyze_screen)
        self.analyze_screen_button.setObjectName("SecondaryButton")
        button_row.addWidget(self.analyze_screen_button)

        right_layout.addLayout(button_row)

        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        self.response_view.setPlaceholderText("AI responses will appear here")
        right_layout.addWidget(self.response_view)

        splitter.addWidget(right_panel)
        splitter.setSizes([200, 400])

        history_label = QLabel("Recent Activity")
        history_label.setObjectName("SubHeaderLabel")
        layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._use_history_item)
        layout.addWidget(self.history_list)

    def _populate_prompts(self):
        self.prompt_list.clear()
        for template in template_manager.templates:
            item = PromptListItem(template)
            self.prompt_list.addItem(item)

    def _populate_history(self):
        self.history_list.clear()
        for entry in reversed(history_manager.history[-20:]):
            item = QListWidgetItem(f"{entry['timestamp']} - {entry['prompt'][:80]}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)

    def _filter_prompts(self, text: str):
        for i in range(self.prompt_list.count()):
            item = self.prompt_list.item(i)
            match = text.lower() in item.text().lower()
            item.setHidden(not match)

    def _on_prompt_selected(self, current: PromptListItem, _previous):
        if not current:
            return
        template = current.template
        self.template_label.setText(f"Template: {template['name']}")
        self.prompt_input.setPlainText(template.get("prompt", ""))

    def _use_history_item(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return
        self.prompt_input.setPlainText(data.get("prompt", ""))
        self.response_view.setPlainText(data.get("response", ""))

    def _run_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        context = self.context_input.toPlainText().strip()
        if not prompt:
            self.response_view.setPlainText("Please enter a prompt.")
            return

        self.run_button.setDisabled(True)
        self.response_view.setPlainText("Running prompt...")
        
        response = self.agent.process_prompt(prompt, context)
        self.response_view.setPlainText(response)

        self.run_button.setDisabled(False)
        self._populate_history()

    def _analyze_screen(self):
        import tempfile
        from datetime import datetime

        temp_dir = tempfile.gettempdir()
        file_name = datetime.now().strftime("agent_screen_%Y%m%d_%H%M%S.png")
        file_path = f"{temp_dir}/{file_name}"

        result = self.agent.system.capture_active_window(file_path)
        if "Failed" in result:
            self.response_view.setPlainText(result)
            return

        analysis = self.agent.analyze_image(file_path, "Analyze the captured screen")
        self.response_view.setPlainText(analysis)

    def focus_input(self):
        self.search_input.setFocus()

    def set_context_text(self, text: str):
        self.context_input.setPlainText(text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            self.context_input.setPlainText(text)
            event.acceptProposedAction()
        elif event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            if not paths:
                return

            if len(paths) == 1:
                try:
                    with open(paths[0], "r", encoding="utf-8") as f:
                        content = f.read()
                    self.context_input.setPlainText(content)
                except Exception:
                    self.context_input.setPlainText(paths[0])
            else:
                self.context_input.setPlainText("\n".join(paths))

            event.acceptProposedAction()

