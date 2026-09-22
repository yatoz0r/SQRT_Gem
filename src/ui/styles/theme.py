"""Modern light and dark theme stylesheets for PySide6 GUI."""

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Roboto', 'Noto Sans', sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #181825;
    color: #a6adc8;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #313244;
    color: #89b4fa;
    font-weight: bold;
}

QLineEdit, QTextEdit, QSpinBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 6px 10px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #89b4fa;
}

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#btn_primary {
    background-color: #89b4fa;
    color: #11111b;
    font-weight: bold;
    border: none;
}

QPushButton#btn_primary:hover {
    background-color: #b4befe;
}

QTableWidget {
    background-color: #181825;
    border: 1px solid #313244;
    gridline-color: #313244;
    color: #cdd6f4;
    selection-background-color: #45475a;
    selection-color: #cdd6f4;
}

QHeaderView::section {
    background-color: #11111b;
    color: #a6adc8;
    padding: 6px;
    border: 1px solid #313244;
    font-weight: bold;
}

QComboBox {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 6px 10px;
}

QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    selection-background-color: #313244;
}

QSlider::groove:horizontal {
    border: 1px solid #45475a;
    height: 6px;
    background: #181825;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #89b4fa;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #cdd6f4;
    border: 1px solid #89b4fa;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f8f9fa;
    color: #212529;
    font-family: 'Segoe UI', 'Roboto', 'Noto Sans', sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #dee2e6;
    background-color: #ffffff;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #e9ecef;
    color: #495057;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #0d6efd;
    font-weight: bold;
}

QLineEdit, QTextEdit, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 6px;
    color: #212529;
    padding: 6px 10px;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #0d6efd;
}

QPushButton {
    background-color: #e9ecef;
    color: #212529;
    border: 1px solid #ced4da;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #dee2e6;
    border-color: #0d6efd;
}

QPushButton#btn_primary {
    background-color: #0d6efd;
    color: #ffffff;
    font-weight: bold;
    border: none;
}

QPushButton#btn_primary:hover {
    background-color: #0b5ed7;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    gridline-color: #f1f3f5;
    color: #212529;
    selection-background-color: #e7f1ff;
    selection-color: #0d6efd;
}

QHeaderView::section {
    background-color: #f1f3f5;
    color: #495057;
    padding: 6px;
    border: 1px solid #dee2e6;
    font-weight: bold;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 6px;
    color: #212529;
    padding: 6px 10px;
}

QSlider::groove:horizontal {
    border: 1px solid #ced4da;
    height: 6px;
    background: #e9ecef;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0d6efd;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #0d6efd;
    width: 14px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 7px;
}
"""

def get_theme_stylesheet(theme_name: str) -> str:
    if theme_name == "dark":
        return DARK_THEME
    elif theme_name == "light":
        return LIGHT_THEME
    # System default: use dark as sleek default
    return DARK_THEME
