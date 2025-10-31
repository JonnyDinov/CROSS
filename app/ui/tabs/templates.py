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
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QMessageBox,
    QComboBox,
)

from app.core.models import Template
from app.core.ollama import OllamaClient
from app.services.world_service import WorldService


class TemplateDialog(QDialog):
    def __init__(
        self,
        parent=None,
        template: Optional[Template] = None,
        ollama: Optional[OllamaClient] = None,
    ):
        super().__init__(parent)
        self.template = template
        self.ollama = ollama
        self.setWindowTitle("Шаблон")

        self.name_edit = QLineEdit()
        self.type_edit = QComboBox()
        self.type_edit.setEditable(True)
        self.type_edit.addItems([
            "character",
            "quest",
            "scene",
            "event",
        ])
        self.content_edit = QTextEdit()
        self.generate_button = QPushButton("✨ Сгенерировать содержимое")

        layout = QFormLayout()
        layout.addRow("Название", self.name_edit)
        layout.addRow("Тип", self.type_edit)
        layout.addRow("Содержимое", self.content_edit)
        layout.addRow("", self.generate_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        self.generate_button.clicked.connect(self.generate_template)

        if template:
            self.name_edit.setText(template.name)
            index = self.type_edit.findText(template.template_type)
            if index >= 0:
                self.type_edit.setCurrentIndex(index)
            else:
                self.type_edit.setEditText(template.template_type)
            self.content_edit.setPlainText(template.content)

    def generate_template(self):
        if not self.ollama:
            return
        template_type = self.type_edit.currentText() or "generic"
        context = self.content_edit.toPlainText().strip()
        prompt = (
            "Ты помогаешь мастеру игр создавать шаблоны."
            f"\nТип шаблона: {template_type}."
        )
        if context:
            prompt += f"\nТекущие заметки:\n{context}"
        prompt += "\n\nСгенерируй структурированный шаблон с ключевыми полями и подсказками."

        result = self.ollama.generate(prompt)
        if result:
            self.content_edit.setPlainText(result.strip())

    def get_data(self) -> Template:
        return Template(
            id=self.template.id if self.template else None,
            name=self.name_edit.text().strip(),
            template_type=self.type_edit.currentText().strip(),
            content=self.content_edit.toPlainText().strip(),
        )


class TemplatesTab(QWidget):
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
        self.detail_label = QLabel("Выберите шаблон")
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
        self.add_button.clicked.connect(self.create_template)
        self.edit_button.clicked.connect(self.edit_template)
        self.delete_button.clicked.connect(self.delete_template)

        self.refresh()

    def _notify_change(self):
        if callable(self.on_change):
            self.on_change()

    def refresh(self):
        self.list_widget.clear()
        templates = self.service.list_templates()
        for template in templates:
            item = QListWidgetItem(f"{template.template_type} / {template.name}")
            item.setData(Qt.UserRole, template)
            self.list_widget.addItem(item)

    def selected_template(self) -> Optional[Template]:
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def show_details(self):
        template = self.selected_template()
        if not template:
            self.detail_label.setText("Выберите шаблон")
            return

        details = [
            f"<b>{template.name}</b>",
            f"Тип: {template.template_type}",
            f"<br>{template.content}",
        ]
        self.detail_label.setText("<br>".join(details))

    def create_template(self):
        dialog = TemplateDialog(self, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            template = dialog.get_data()
            self.service.save_template(template)
            self.refresh()
            self._notify_change()

    def edit_template(self):
        template = self.selected_template()
        if not template:
            QMessageBox.warning(self, "Шаблоны", "Выберите шаблон для редактирования")
            return

        dialog = TemplateDialog(self, template, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            self.service.save_template(updated)
            self.refresh()
            self._notify_change()

    def delete_template(self):
        template = self.selected_template()
        if not template:
            return

        confirm = QMessageBox.question(
            self,
            "Удаление шаблона",
            f"Удалить {template.name}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_template(template.id)
            self.refresh()
            self._notify_change()
