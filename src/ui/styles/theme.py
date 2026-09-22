"""Refined, modern theme stylesheets crafted with Emil Kowalski's design engineering philosophy.
Features subtle depth, intentional visual hierarchy, tactile button feedback, and crisp typography.
"""

DARK_THEME = """
/* Global Window & Base Typography */
QMainWindow, QWidget {
    background-color: #0d0e12;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    font-size: 13px;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}

/* Modern Segmented Tab Bar */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.07);
    background-color: #121318;
    border-radius: 12px;
    padding: 2px;
}

QTabBar {
    background: transparent;
    qproperty-drawBase: 0;
    margin-bottom: 8px;
}

QTabBar::tab {
    background-color: transparent;
    color: #94a3b8;
    padding: 8px 18px;
    margin-right: 4px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
}

QTabBar::tab:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
}

QTabBar::tab:selected {
    background-color: #1e2028;
    color: #ffffff;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Input Fields with Subtle Glow & Clean Padding */
QLineEdit {
    background-color: #16181f;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #f8fafc;
    padding: 10px 14px;
    font-size: 15px;
}

QLineEdit:hover {
    border-color: rgba(255, 255, 255, 0.18);
}

QLineEdit:focus {
    border: 1px solid #6366f1;
    background-color: #181a23;
}

/* Result Screen (Receipt / Monospace Surface) */
QTextEdit#result_display {
    background-color: #090a0d;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #38bdf8;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 15px;
    line-height: 1.4;
    padding: 12px;
    selection-background-color: rgba(56, 189, 248, 0.3);
}

/* Secondary TextEdits & Log Viewers */
QTextEdit, QTextBrowser {
    background-color: #14151b;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    color: #cbd5e1;
    padding: 10px;
    font-size: 13px;
}

/* Modern Keypad Buttons Hierarchy */
QPushButton {
    background-color: #1c1e27;
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #262935;
    border-color: rgba(255, 255, 255, 0.16);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #161820;
    padding-top: 10px;
    padding-bottom: 6px;
}

/* Numerical Keys: Neutral, solid, clean */
QPushButton#btn_num {
    background-color: #181921;
    color: #f1f5f9;
    font-size: 16px;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_num:hover {
    background-color: #232531;
    border-color: rgba(255, 255, 255, 0.15);
}

QPushButton#btn_num:pressed {
    background-color: #121319;
    padding-top: 10px;
}

/* Operators (+, -, *, /, ^): Distinct soft slate surface */
QPushButton#btn_op {
    background-color: #1e2230;
    color: #93c5fd;
    font-size: 15px;
    font-weight: 600;
    border: 1px solid rgba(147, 197, 253, 0.15);
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_op:hover {
    background-color: #292f44;
    border-color: rgba(147, 197, 253, 0.3);
    color: #bfdbfe;
}

QPushButton#btn_op:pressed {
    background-color: #181a26;
    padding-top: 10px;
}

/* Advanced Functions (sqrt, abs, ln, exp, pi, e): Subtle Violet Tint */
QPushButton#btn_func {
    background-color: #201f2e;
    color: #c4b5fd;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid rgba(196, 181, 253, 0.15);
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_func:hover {
    background-color: #2d2a42;
    border-color: rgba(196, 181, 253, 0.3);
    color: #ddd6fe;
}

QPushButton#btn_func:pressed {
    background-color: #181724;
    padding-top: 10px;
}

/* Action Button: Clear (C) - Restrained Coral / Danger */
QPushButton#btn_clear {
    background-color: rgba(239, 68, 68, 0.12);
    color: #fca5a5;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_clear:hover {
    background-color: rgba(239, 68, 68, 0.22);
    border-color: rgba(239, 68, 68, 0.4);
    color: #fecaca;
}

QPushButton#btn_clear:pressed {
    background-color: rgba(239, 68, 68, 0.08);
    padding-top: 10px;
}

/* Action Button: Equals (=) - Confident Indigo Primary Accent */
QPushButton#btn_primary, QPushButton#btn_equals {
    background-color: #6366f1;
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_primary:hover, QPushButton#btn_equals:hover {
    background-color: #4f46e5;
}

QPushButton#btn_primary:pressed, QPushButton#btn_equals:pressed {
    background-color: #4338ca;
    padding-top: 10px;
}

/* Card Containers & Group Boxes */
QFrame#surface_card {
    background-color: #14151c;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px;
}

/* Precision Slider (Crafted Track & Thumb) */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #232532;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #6366f1;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #6366f1;
    width: 16px;
    height: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #e0e7ff;
    transform: scale(1.1);
}

/* SpinBox */
QSpinBox {
    background-color: #181a23;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #f8fafc;
    padding: 6px 8px;
    font-weight: 600;
}

QSpinBox:focus {
    border-color: #6366f1;
}

/* History Table with Crisp Headers & Row Hover */
QTableWidget {
    background-color: #101116;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    gridline-color: rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
    selection-background-color: rgba(99, 102, 241, 0.25);
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #161821;
    color: #94a3b8;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-weight: 600;
    font-size: 12px;
}

QTableWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.02);
}

QTableWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

/* ComboBoxes */
QComboBox {
    background-color: #181a23;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #f1f5f9;
    padding: 8px 12px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: rgba(255, 255, 255, 0.2);
}

QComboBox QAbstractItemView {
    background-color: #181a23;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: #f1f5f9;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
    padding: 4px;
}

/* Status Bar */
QStatusBar {
    background-color: #0d0e12;
    color: #64748b;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 12px;
}
"""

LIGHT_THEME = """
/* Global Window & Base Typography */
QMainWindow, QWidget {
    background-color: #f8fafc;
    color: #0f172a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    font-size: 13px;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
}

/* Modern Segmented Tab Bar */
QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    border-radius: 12px;
    padding: 2px;
}

QTabBar {
    background: transparent;
    qproperty-drawBase: 0;
    margin-bottom: 8px;
}

QTabBar::tab {
    background-color: transparent;
    color: #64748b;
    padding: 8px 18px;
    margin-right: 4px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
}

QTabBar::tab:hover {
    background-color: #f1f5f9;
    color: #1e293b;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #4f46e5;
    font-weight: 600;
    border: 1px solid #cbd5e1;
}

/* Input Fields */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    color: #0f172a;
    padding: 10px 14px;
    font-size: 15px;
}

QLineEdit:hover {
    border-color: #94a3b8;
}

QLineEdit:focus {
    border: 1px solid #4f46e5;
    background-color: #ffffff;
}

/* Result Screen */
QTextEdit#result_display {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    color: #38bdf8;
    font-family: "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 15px;
    line-height: 1.4;
    padding: 12px;
}

QTextEdit, QTextBrowser {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #334155;
    padding: 10px;
}

/* Buttons Hierarchy */
QPushButton {
    background-color: #f1f5f9;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #e2e8f0;
    color: #0f172a;
}

QPushButton:pressed {
    background-color: #cbd5e1;
    padding-top: 10px;
    padding-bottom: 6px;
}

/* Numerical Keys */
QPushButton#btn_num {
    background-color: #ffffff;
    color: #0f172a;
    font-size: 16px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_num:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
}

QPushButton#btn_num:pressed {
    background-color: #f1f5f9;
    padding-top: 10px;
}

/* Operators */
QPushButton#btn_op {
    background-color: #eff6ff;
    color: #1d4ed8;
    font-size: 15px;
    font-weight: 600;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_op:hover {
    background-color: #dbeafe;
    color: #1e40af;
}

QPushButton#btn_op:pressed {
    background-color: #bfdbfe;
    padding-top: 10px;
}

/* Advanced Functions */
QPushButton#btn_func {
    background-color: #faf5ff;
    color: #7e22ce;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #e9d5ff;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_func:hover {
    background-color: #f3e8ff;
    color: #6b21a8;
}

QPushButton#btn_func:pressed {
    background-color: #e9d5ff;
    padding-top: 10px;
}

/* Action: Clear */
QPushButton#btn_clear {
    background-color: #fff1f2;
    color: #e11d48;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #fecdd3;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_clear:hover {
    background-color: #ffe4e6;
}

QPushButton#btn_clear:pressed {
    background-color: #fecdd3;
    padding-top: 10px;
}

/* Action: Equals */
QPushButton#btn_primary, QPushButton#btn_equals {
    background-color: #4f46e5;
    color: #ffffff;
    font-size: 16px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    min-height: 42px;
}

QPushButton#btn_primary:hover, QPushButton#btn_equals:hover {
    background-color: #4338ca;
}

QPushButton#btn_primary:pressed, QPushButton#btn_equals:pressed {
    background-color: #3730a3;
    padding-top: 10px;
}

/* Card Containers */
QFrame#surface_card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #4f46e5;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #4f46e5;
    width: 16px;
    height: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

/* SpinBox */
QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    color: #0f172a;
    padding: 6px 8px;
}

/* Table */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: #f1f5f9;
    color: #1e293b;
    selection-background-color: #e0e7ff;
    selection-color: #3730a3;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #64748b;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    font-weight: 600;
    font-size: 12px;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    color: #0f172a;
    padding: 8px 12px;
}

/* Status Bar */
QStatusBar {
    background-color: #f8fafc;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    font-size: 12px;
}
"""

def get_theme_stylesheet(theme_name: str) -> str:
    if theme_name == "light":
        return LIGHT_THEME
    return DARK_THEME
