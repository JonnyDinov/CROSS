from typing import Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QApplication,
)

from app.core.models import LoreItem
from app.core.ollama import OllamaClient
from app.services.world_service import WorldService
from app.ui.components.generative_fields import GenerativeLineEdit, GenerativeTextEdit


class LoreDialog(QDialog):
    def __init__(
        self,
        parent=None,
        lore: Optional[LoreItem] = None,
        ollama: Optional[OllamaClient] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Лор")
        self.lore = lore
        self.ollama = ollama

        self.category_edit = GenerativeLineEdit()
        self.title_edit = GenerativeLineEdit()
        self.summary_edit = GenerativeTextEdit(height=100)
        self.details_edit = GenerativeTextEdit(height=140)
        self.relations_edit = GenerativeTextEdit(height=80)

        layout = QFormLayout()
        layout.addRow("Категория", self.category_edit)
        layout.addRow("Название", self.title_edit)
        layout.addRow("Краткое описание", self.summary_edit)
        layout.addRow("Подробности", self.details_edit)
        layout.addRow("Связи", self.relations_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        self.category_edit.request_generate.connect(lambda: self.generate_field("category"))
        self.title_edit.request_generate.connect(lambda: self.generate_field("title"))
        self.summary_edit.request_generate.connect(lambda: self.generate_field("summary"))
        self.details_edit.request_generate.connect(lambda: self.generate_field("details"))
        self.relations_edit.request_generate.connect(lambda: self.generate_field("relations"))

        if lore:
            self.category_edit.setText(lore.category)
            self.title_edit.setText(lore.title)
            self.summary_edit.setPlainText(lore.summary)
            self.details_edit.setPlainText(lore.details)
            self.relations_edit.setPlainText(lore.relations)

    def _context(self) -> str:
        parts = []
        if self.category_edit.text().strip():
            parts.append(f"Категория: {self.category_edit.text().strip()}")
        if self.title_edit.text().strip():
            parts.append(f"Название: {self.title_edit.text().strip()}")
        summary = self.summary_edit.toPlainText().strip()
        if summary:
            parts.append(f"Краткое описание: {summary}")
        details = self.details_edit.toPlainText().strip()
        if details:
            parts.append(f"Подробности: {details}")
        relations = self.relations_edit.toPlainText().strip()
        if relations:
            parts.append(f"Связи: {relations}")
        return "\n".join(parts)

    def generate_field(self, field: str):
        if not self.ollama:
            return
        instructions = {
            "category": "Определи подходящую категорию (например, локация, фракция, артефакт, событие).",
            "title": "Придумай выразительное название для элемента лора.",
            "summary": "Кратко опиши этот элемент лора в 2-3 предложениях.",
            "details": "Раскрой подробности и уникальные особенности, добавь атмосферности.",
            "relations": "Опиши связи с другими элементами мира, персонажами или событиями.",
        }
        instruction = instructions.get(field)
        if not instruction:
            return
        context = self._context()
        prompt = "Ты мастер лора."
        if context:
            prompt += f"\nИзвестные сведения:\n{context}"
        prompt += f"\n\n{instruction}\nОтвет предоставь связным текстом."

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            result = self.ollama.generate(prompt)
        finally:
            QApplication.restoreOverrideCursor()
        if not result:
            return

        setter_map = {
            "category": self.category_edit.setText,
            "title": self.title_edit.setText,
            "summary": self.summary_edit.setPlainText,
            "details": self.details_edit.setPlainText,
            "relations": self.relations_edit.setPlainText,
        }
        setter = setter_map.get(field)
        if setter:
            setter(result.strip())

    def get_data(self) -> LoreItem:
        return LoreItem(
            id=self.lore.id if self.lore else None,
            category=self.category_edit.text().strip(),
            title=self.title_edit.text().strip(),
            summary=self.summary_edit.toPlainText().strip(),
            details=self.details_edit.toPlainText().strip(),
            relations=self.relations_edit.toPlainText().strip(),
        )


class LoreTab(QWidget):
    def __init__(
        self,
        service: WorldService,
        ollama: OllamaClient,
        on_change: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.service = service
        self.ollama = ollama
        self.on_change = on_change

        self.list_widget = QListWidget()
        self.detail_label = QLabel("Выберите запись лора")
        self.detail_label.setWordWrap(True)

        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(self.detail_label)
        self.setLayout(layout)

        self.list_widget.itemSelectionChanged.connect(self.show_details)
        self.add_button.clicked.connect(self.create_lore)
        self.edit_button.clicked.connect(self.edit_lore)
        self.delete_button.clicked.connect(self.delete_lore)

        self.refresh()

    def _notify_change(self):
        if callable(self.on_change):
            self.on_change()

    def refresh(self):
        self.list_widget.clear()
        lore_items = self.service.list_lore()
        for lore in lore_items:
            item = QListWidgetItem(f"{lore.category} / {lore.title}")
            item.setData(Qt.UserRole, lore)
            self.list_widget.addItem(item)

    def selected_lore(self) -> Optional[LoreItem]:
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def show_details(self):
        lore = self.selected_lore()
        if not lore:
            self.detail_label.setText("Выберите запись лора")
            return

        details = [
            f"<b>{lore.title}</b>",
            f"Категория: {lore.category}",
            f"<br>{lore.summary}",
            f"<br>{lore.details}",
        ]
        self.detail_label.setText("<br>".join(details))

    def create_lore(self):
        dialog = LoreDialog(self, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            lore = dialog.get_data()
            self.service.save_lore(lore)
            self.refresh()
            self._notify_change()

    def edit_lore(self):
        lore = self.selected_lore()
        if not lore:
            QMessageBox.warning(self, "Лор", "Выберите запись для редактирования")
            return

        dialog = LoreDialog(self, lore, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            self.service.save_lore(updated)
            self.refresh()
            self._notify_change()

    def delete_lore(self):
        lore = self.selected_lore()
        if not lore:
            return

        confirm = QMessageBox.question(
            self,
            "Удаление лора",
            f"Удалить {lore.title}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_lore(lore.id)
            self.refresh()
            self._notify_change()
