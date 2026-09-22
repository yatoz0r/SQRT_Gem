"""Settings Tab for language selection, themes, default precision, and update checks."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QSpinBox, QCheckBox, QPushButton, QLabel,
    QMessageBox, QFrame
)
from src.storage import ConfigManager, AppConfig
from src.i18n import tr, SUPPORTED_LANGUAGES, LocalizationService
from src.updater import UpdateChecker, UpdateInfo

class SettingsTab(QWidget):
    """Tab managing user preferences, themes, language, and update triggers."""

    theme_changed = Signal(str)
    language_changed = Signal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.updater = UpdateChecker()
        self.i18n = LocalizationService()

        self._init_ui()
        self._load_values()
        self.retranslate_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_title)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.02); border-radius: 8px; padding: 12px;")
        form = QFormLayout(form_frame)
        form.setSpacing(14)

        # 1. Language selector
        self.lbl_lang = QLabel()
        self.combo_lang = QComboBox()
        for code, name in SUPPORTED_LANGUAGES:
            self.combo_lang.addItem(name, code)
        self.combo_lang.currentIndexChanged.connect(self._on_language_selected)
        form.addRow(self.lbl_lang, self.combo_lang)

        # 2. Theme selector
        self.lbl_theme = QLabel()
        self.combo_theme = QComboBox()
        self.combo_theme.addItem("System", "system")
        self.combo_theme.addItem("Light", "light")
        self.combo_theme.addItem("Dark", "dark")
        self.combo_theme.currentIndexChanged.connect(self._on_theme_selected)
        form.addRow(self.lbl_theme, self.combo_theme)

        # 3. Default precision
        self.lbl_def_prec = QLabel()
        self.spin_def_prec = QSpinBox()
        self.spin_def_prec.setRange(0, 1000)
        form.addRow(self.lbl_def_prec, self.spin_def_prec)

        # 4. Auto-update checkbox
        self.chk_auto_update = QCheckBox()
        form.addRow("", self.chk_auto_update)

        layout.addWidget(form_frame)

        # Update Checker Section
        update_frame = QFrame()
        update_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.02); border-radius: 8px; padding: 12px;")
        up_layout = QHBoxLayout(update_frame)

        self.lbl_update_status = QLabel(tr("update_title"))
        up_layout.addWidget(self.lbl_update_status)

        up_layout.addStretch()
        self.btn_check_update = QPushButton()
        self.btn_check_update.clicked.connect(self._check_updates)
        up_layout.addWidget(self.btn_check_update)

        layout.addWidget(update_frame)

        # Save Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_save = QPushButton()
        self.btn_save.setObjectName("btn_primary")
        self.btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def _load_values(self):
        cfg = self.config_manager.config
        # Set language combo
        idx = self.combo_lang.findData(cfg.language)
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)

        # Set theme combo
        idx_t = self.combo_theme.findData(cfg.theme)
        if idx_t >= 0:
            self.combo_theme.setCurrentIndex(idx_t)

        self.spin_def_prec.setValue(cfg.default_precision)
        self.chk_auto_update.setChecked(cfg.auto_check_updates)

    def _on_language_selected(self, index: int):
        code = self.combo_lang.itemData(index)
        if code:
            self.i18n.set_language(code)
            self.config_manager.config.language = code
            self.config_manager.save_config()
            self.language_changed.emit(code)

    def _on_theme_selected(self, index: int):
        theme = self.combo_theme.itemData(index)
        if theme:
            self.config_manager.config.theme = theme
            self.config_manager.save_config()
            self.theme_changed.emit(theme)

    def _save_settings(self):
        self.config_manager.config.default_precision = self.spin_def_prec.value()
        self.config_manager.config.auto_check_updates = self.chk_auto_update.isChecked()
        self.config_manager.save_config()
        QMessageBox.information(self, "Settings", tr("settings_saved_success"))

    def _check_updates(self):
        info: UpdateInfo = self.updater.check_for_updates()
        if info.available:
            type_label = tr("update_type_critical") if info.update_type == "critical" else tr("update_type_feature")
            msg = (
                f"{tr('update_available', new_version=info.latest_version, current_version=info.current_version)}\n\n"
                f"Type: {type_label}\n"
                f"Changelog: {info.changelog}\n\n"
                f"Download: {info.download_url}"
            )
            QMessageBox.information(self, tr("update_title"), msg)
        else:
            QMessageBox.information(self, tr("update_title"), tr("update_latest", version=info.current_version))

    def retranslate_ui(self):
        self.lbl_title.setText(tr("settings_title"))
        self.lbl_lang.setText(tr("settings_language"))
        self.lbl_theme.setText(tr("settings_theme"))
        self.lbl_def_prec.setText(tr("settings_default_precision"))
        self.chk_auto_update.setText(tr("settings_auto_updates"))
        self.btn_save.setText(tr("settings_save"))
        self.btn_check_update.setText(tr("update_btn_check"))
        self.lbl_update_status.setText(tr("update_title"))
