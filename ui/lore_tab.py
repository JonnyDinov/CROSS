from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox

from modules import lore_manager


class LoreTab(QWidget):
    lore_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.lore_text = QTextEdit(self)
        self.lore_text.setPlaceholderText("Редактируйте лор мира здесь...")
        self.layout.addWidget(self.lore_text)

        self.save_button = QPushButton("Сохранить изменения", self)
        self.save_button.clicked.connect(self.save_lore)
        self.layout.addWidget(self.save_button)

        self.refresh_button = QPushButton("Обновить контекст", self)
        self.refresh_button.clicked.connect(self.load_lore)
        self.layout.addWidget(self.refresh_button)

        self.load_lore()

    def load_lore(self) -> None:
        try:
            lore = lore_manager.get_lore()
            self.lore_text.setPlainText(lore)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def save_lore(self) -> None:
        try:
            content = self.lore_text.toPlainText()
            lore_manager.save_lore(content)
            QMessageBox.information(self, "Успех", "Лор успешно сохранён")
            self.lore_updated.emit(content)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
