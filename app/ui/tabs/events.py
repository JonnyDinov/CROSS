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
    QDialogButtonBox,
    QMessageBox,
    QComboBox,
    QApplication,
)

from app.core.models import Event
from app.core.ollama import OllamaClient
from app.services.world_service import WorldService
from app.ui.components.generative_fields import GenerativeLineEdit, GenerativeTextEdit


class EventDialog(QDialog):
    def __init__(
        self,
        parent=None,
        event: Optional[Event] = None,
        ollama: Optional[OllamaClient] = None,
    ):
        super().__init__(parent)
        self.event = event
        self.ollama = ollama
        self.setWindowTitle("Событие")

        self.title_edit = GenerativeLineEdit()
        self.location_edit = GenerativeLineEdit()
        self.participants_edit = QLineEdit()
        self.status_edit = QComboBox()
        self.status_edit.addItems(["planned", "in_progress", "completed"])
        self.description_edit = GenerativeTextEdit(height=120)
        self.consequences_edit = GenerativeTextEdit(height=120)

        layout = QFormLayout()
        layout.addRow("Название", self.title_edit)
        layout.addRow("Локация", self.location_edit)
        layout.addRow("Участники", self.participants_edit)
        layout.addRow("Статус", self.status_edit)
        layout.addRow("Описание", self.description_edit)
        layout.addRow("Последствия", self.consequences_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        self.title_edit.request_generate.connect(lambda: self.generate_field("title"))
        self.location_edit.request_generate.connect(lambda: self.generate_field("location"))
        self.description_edit.request_generate.connect(lambda: self.generate_field("description"))
        self.consequences_edit.request_generate.connect(lambda: self.generate_field("consequences"))

        if event:
            self.title_edit.setText(event.title)
            self.location_edit.setText(event.location)
            self.participants_edit.setText(event.participants)
            index = self.status_edit.findText(event.status)
            if index >= 0:
                self.status_edit.setCurrentIndex(index)
            self.description_edit.setPlainText(event.description)
            self.consequences_edit.setPlainText(event.consequences)

    def _context(self) -> str:
        parts = []
        if self.title_edit.text():
            parts.append(f"Название: {self.title_edit.text().strip()}")
        if self.location_edit.text():
            parts.append(f"Локация: {self.location_edit.text().strip()}")
        if self.participants_edit.text():
            parts.append(f"Участники: {self.participants_edit.text().strip()}")
        desc = self.description_edit.toPlainText().strip()
        if desc:
            parts.append(f"Описание: {desc}")
        conseq = self.consequences_edit.toPlainText().strip()
        if conseq:
            parts.append(f"Последствия: {conseq}")
        return "\n".join(parts)

    def generate_field(self, field: str):
        if not self.ollama:
            return
        instructions = {
            "title": "Сформулируй захватывающее название события.",
            "location": "Предложи атмосферную локацию для события.",
            "description": "Опиши событие, его ход и атмосферу.",
            "consequences": "Опиши последствия события и влияния на мир.",
        }
        instruction = instructions.get(field)
        if not instruction:
            return
        context = self._context()
        prompt = "Ты хронист ролевого мира."
        if context:
            prompt += f"\nИзвестные детали:\n{context}"
        prompt += f"\n\n{instruction}\nОтвет должен быть информативным."

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            result = self.ollama.generate(prompt)
        finally:
            QApplication.restoreOverrideCursor()
        if not result:
            return

        setter_map = {
            "title": self.title_edit.setText,
            "location": self.location_edit.setText,
            "description": self.description_edit.setPlainText,
            "consequences": self.consequences_edit.setPlainText,
        }
        setter = setter_map.get(field)
        if setter:
            setter(result.strip())

    def get_data(self) -> Event:
        return Event(
            id=self.event.id if self.event else None,
            title=self.title_edit.text().strip(),
            location=self.location_edit.text().strip(),
            participants=self.participants_edit.text().strip(),
            status=self.status_edit.currentText(),
            description=self.description_edit.toPlainText().strip(),
            consequences=self.consequences_edit.toPlainText().strip(),
        )


class EventsTab(QWidget):
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
        self.detail_label = QLabel("Выберите событие")
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
        self.add_button.clicked.connect(self.create_event)
        self.edit_button.clicked.connect(self.edit_event)
        self.delete_button.clicked.connect(self.delete_event)

        self.refresh()

    def _notify_change(self):
        if callable(self.on_change):
            self.on_change()

    def refresh(self):
        self.list_widget.clear()
        events = self.service.list_events()
        for event in events:
            item = QListWidgetItem(event.title)
            item.setData(Qt.UserRole, event)
            self.list_widget.addItem(item)

    def selected_event(self) -> Optional[Event]:
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def show_details(self):
        event = self.selected_event()
        if not event:
            self.detail_label.setText("Выберите событие")
            return

        details = [
            f"<b>{event.title}</b>",
            f"Локация: {event.location}",
            f"Участники: {event.participants}",
            f"Статус: {event.status}",
            f"Описание: {event.description}",
            f"Последствия: {event.consequences}",
        ]
        self.detail_label.setText("<br>".join(details))

    def create_event(self):
        dialog = EventDialog(self, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            event = dialog.get_data()
            self.service.save_event(event)
            self.refresh()
            self._notify_change()

    def edit_event(self):
        event = self.selected_event()
        if not event:
            QMessageBox.warning(self, "События", "Выберите событие для редактирования")
            return

        dialog = EventDialog(self, event, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            self.service.save_event(updated)
            self.refresh()
            self._notify_change()

    def delete_event(self):
        event = self.selected_event()
        if not event:
            return

        confirm = QMessageBox.question(
            self,
            "Удаление события",
            f"Удалить {event.title}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_event(event.id)
            self.refresh()
            self._notify_change()

