"""Main application window connecting calculator, history, settings, and diagnostics."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QApplication
)
from src.storage import ConfigManager, HistoryManager
from src.i18n import LocalizationService, tr
from src.ui.styles.theme import get_theme_stylesheet
from src.ui.tabs.calculator_tab import CalculatorTab
from src.ui.tabs.history_tab import HistoryTab
from src.ui.tabs.settings_tab import SettingsTab
from src.ui.tabs.diagnostics_tab import DiagnosticsTab

class MainWindow(QMainWindow):
    """Main window coordinating all primary tabs, application state, and theme styling."""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.history_manager = HistoryManager()
        self.i18n = LocalizationService(default_lang=self.config_manager.config.language)

        self._init_ui()
        self._apply_theme(self.config_manager.config.theme)
        self.i18n.subscribe(self._on_language_changed)

        if self.config_manager.config.auto_check_updates:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, self._background_check_updates)

    def _init_ui(self):
        self.resize(940, 720)
        self.setMinimumSize(800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 1. Calculator Tab
        self.tab_calculator = CalculatorTab(
            history_manager=self.history_manager,
            default_precision=self.config_manager.config.default_precision
        )
        self.tab_calculator.calculation_completed.connect(self._on_calculation_completed)

        # 2. History Tab
        self.tab_history = HistoryTab(history_manager=self.history_manager)
        self.tab_history.reuse_requested.connect(self._on_history_reuse)

        # 3. Settings Tab
        self.tab_settings = SettingsTab(config_manager=self.config_manager)
        self.tab_settings.theme_changed.connect(self._apply_theme)
        self.tab_settings.language_changed.connect(self._on_language_changed)

        # 4. Diagnostics Tab
        self.tab_diagnostics = DiagnosticsTab()

        self.tabs.addTab(self.tab_calculator, "")
        self.tabs.addTab(self.tab_history, "")
        self.tabs.addTab(self.tab_settings, "")
        self.tabs.addTab(self.tab_diagnostics, "")

        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.retranslate_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.tab_calculator.txt_expression.setFocus()

    def _on_tab_changed(self, index: int):
        if index == 0:
            self.tab_calculator.txt_expression.setFocus()

    def keyPressEvent(self, event):
        if self.tabs.currentIndex() == 0:
            if not self.tab_calculator.txt_expression.hasFocus():
                self.tab_calculator.keyPressEvent(event)
                if event.isAccepted():
                    return
        super().keyPressEvent(event)

    def _on_calculation_completed(self, result):
        self.tab_history.refresh_table()
        self.status_bar.showMessage(f"Calculation done in {result.elapsed_ms} ms", 3000)

    def _on_history_reuse(self, expression: str, precision: int):
        self.tab_calculator.set_expression(expression, precision)
        self.tabs.setCurrentIndex(0)

    def _apply_theme(self, theme_name: str):
        style = get_theme_stylesheet(theme_name)
        qapp = QApplication.instance()
        if qapp:
            qapp.setStyleSheet(style)

    def _on_language_changed(self, lang_code: str):
        self.retranslate_ui()
        self.tab_calculator.retranslate_ui()
        self.tab_history.retranslate_ui()
        self.tab_settings.retranslate_ui()
        self.tab_diagnostics.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(tr("app_title"))
        self.tabs.setTabText(0, tr("tab_calculator"))
        self.tabs.setTabText(1, tr("tab_history"))
        self.tabs.setTabText(2, tr("tab_settings"))
        self.tabs.setTabText(3, tr("tab_diagnostics"))

    def _background_check_updates(self):
        try:
            from src.updater import UpdateChecker
            updater = UpdateChecker(current_version=self.config_manager.config.version)
            info = updater.check_for_updates()
            if info.available:
                from src.ui.dialogs.update_dialog import UpdateDialog
                dlg = UpdateDialog(self, update_info=info)
                dlg.exec()
        except Exception:
            pass
