#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("World Builder")
    app.setApplicationDisplayName("World Builder with Ollama")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
