DARK_THEME_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Ubuntu", sans-serif;
    font-size: 10pt;
}

QTabWidget::pane {
    border: 1px solid #333;
    background-color: #252525;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #a0a0a0;
    padding: 8px 16px;
    border: 1px solid #3a3a3a;
    border-bottom: none;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #252525;
    color: #e0e0e0;
    border-bottom: 2px solid #3498db;
}

QTabBar::tab:hover {
    background-color: #333;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f618d;
}

QPushButton:disabled {
    background-color: #555;
    color: #888;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    padding: 6px;
    border-radius: 3px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3498db;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #e0e0e0;
    margin-right: 6px;
}

QListWidget, QTreeWidget, QTableWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    alternate-background-color: #333;
}

QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {
    background-color: #444;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 14px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #555;
    border-radius: 7px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666;
}

QScrollBar:horizontal {
    background-color: #2d2d2d;
    height: 14px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #555;
    border-radius: 7px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666;
}

QLabel {
    color: #e0e0e0;
}

QGroupBox {
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #3498db;
}

QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #3498db;
}

QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
}

QMenu::item:selected {
    background-color: #3498db;
}

QStatusBar {
    background-color: #252525;
    color: #a0a0a0;
}

QToolTip {
    background-color: #3a3a3a;
    color: #e0e0e0;
    border: 1px solid #555;
}
"""
