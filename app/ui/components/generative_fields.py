from typing import Callable, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
)


class GenerativeMixin:
    generated = pyqtSignal(str)

    def __init__(self, *args, generator_callback: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._generator_callback = generator_callback

    def _emit_generate(self):
        if callable(self._generator_callback):
            self._generator_callback()


class GenerativeLineEdit(QWidget):
    request_generate = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_edit = QLineEdit()
        self.generate_button = QPushButton("✨")
        self.generate_button.setFixedWidth(36)
        self.generate_button.clicked.connect(self.request_generate.emit)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.generate_button)
        self.setLayout(layout)

    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, text: str):
        self.line_edit.setText(text)


class GenerativeTextEdit(QWidget):
    request_generate = pyqtSignal()

    def __init__(self, parent=None, height: int = 120):
        super().__init__(parent)
        self.text_edit = QTextEdit()
        self.text_edit.setFixedHeight(height)
        self.generate_button = QPushButton("✨ Сгенерировать")
        self.generate_button.setFixedWidth(140)
        self.generate_button.clicked.connect(self.request_generate.emit)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.text_edit)
        layout.addWidget(self.generate_button)
        self.setLayout(layout)

    def toPlainText(self) -> str:
        return self.text_edit.toPlainText()

    def setPlainText(self, text: str):
        self.text_edit.setPlainText(text)

    def clear(self):
        self.text_edit.clear()
