DARK_THEME = """
/* Main Window */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

/* Prompt Panel */
QWidget#PromptPanel {
    background-color: #2d2d30;
    border-radius: 12px;
    border: 1px solid #3e3e42;
}

/* Search Input */
QLineEdit {
    background-color: #3e3e42;
    border: 2px solid #555555;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 14px;
    color: #e0e0e0;
}

QLineEdit:focus {
    border: 2px solid #007acc;
}

/* Text Edit */
QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
    color: #e0e0e0;
    font-family: 'Consolas', 'Monaco', monospace;
}

/* Buttons */
QPushButton {
    background-color: #007acc;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #005a9e;
}

QPushButton:pressed {
    background-color: #004578;
}

QPushButton:disabled {
    background-color: #3e3e42;
    color: #808080;
}

QPushButton#SecondaryButton {
    background-color: #3e3e42;
    color: #e0e0e0;
}

QPushButton#SecondaryButton:hover {
    background-color: #505050;
}

QPushButton#DangerButton {
    background-color: #d32f2f;
}

QPushButton#DangerButton:hover {
    background-color: #b71c1c;
}

/* List Widget */
QListWidget {
    background-color: #252526;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    outline: none;
}

QListWidget::item {
    padding: 12px;
    border-bottom: 1px solid #3e3e42;
    color: #e0e0e0;
}

QListWidget::item:hover {
    background-color: #2a2d2e;
}

QListWidget::item:selected {
    background-color: #094771;
    border-left: 3px solid #007acc;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Combo Box */
QComboBox {
    background-color: #3e3e42;
    border: 2px solid #555555;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e0e0e0;
}

QComboBox:hover {
    border: 2px solid #007acc;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    selection-background-color: #094771;
    color: #e0e0e0;
}

/* Labels */
QLabel {
    color: #e0e0e0;
    font-size: 13px;
}

QLabel#HeaderLabel {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
}

QLabel#SubHeaderLabel {
    font-size: 14px;
    font-weight: 500;
    color: #cccccc;
}

QLabel#CategoryLabel {
    font-size: 11px;
    color: #888888;
    text-transform: uppercase;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #3e3e42;
    border-radius: 8px;
    background-color: #2d2d30;
}

QTabBar::tab {
    background-color: #3e3e42;
    color: #e0e0e0;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #505050;
}

/* Check Box */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #555555;
    background-color: #3e3e42;
}

QCheckBox::indicator:checked {
    background-color: #007acc;
    border-color: #007acc;
}

QCheckBox::indicator:hover {
    border-color: #007acc;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #3e3e42;
    border: 2px solid #555555;
    border-radius: 8px;
    padding: 8px;
    color: #e0e0e0;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #007acc;
}

/* Group Box */
QGroupBox {
    border: 1px solid #3e3e42;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 500;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 5px;
}

/* Tooltips */
QToolTip {
    background-color: #2d2d30;
    color: #e0e0e0;
    border: 1px solid #3e3e42;
    border-radius: 6px;
    padding: 6px;
}

/* Menu */
QMenu {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #094771;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: white;
    border-top: 1px solid #005a9e;
}
"""
