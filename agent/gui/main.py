from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from agent.config import config
from agent.core.agent import agent
from agent.core.logging import configure_logging
from agent.gui.views.main_window import MainWindow


def run():
    configure_logging(config.get("agent.log_level", "INFO"))
    logging.getLogger(__name__).info("Starting GUI application")

    app = QApplication(sys.argv)
    app.setApplicationName("Windows AI Agent")
    app.setWindowIcon(QIcon())  # Placeholder, load actual SVG icon if available

    window = MainWindow(agent)
    window.show()

    sys.exit(app.exec())


__all__ = ["run"]
