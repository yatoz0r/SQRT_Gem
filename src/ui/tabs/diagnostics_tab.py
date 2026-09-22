"""Diagnostics & Self-Service Tab implementing Section 13 support-cost reduction features."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QTextBrowser,
    QMessageBox, QHeaderView, QFrame
)
from src.diagnostics import HealthChecker, HealthReport, ReportGenerator, RecoveryManager, get_faq_items
from src.i18n import tr

class DiagnosticsTab(QWidget):
    """Tab providing automated self-checks, support bundle export, factory reset, and troubleshooting FAQ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.health_checker = HealthChecker()
        self.report_generator = ReportGenerator()
        self.recovery_manager = RecoveryManager()

        self._init_ui()
        self.retranslate_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel()
        self.lbl_subtitle.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(self.lbl_subtitle)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_run_check = QPushButton()
        self.btn_run_check.setObjectName("btn_primary")
        self.btn_run_check.setMinimumHeight(38)
        self.btn_run_check.clicked.connect(self._run_health_check)
        btn_bar.addWidget(self.btn_run_check)

        self.btn_export_bundle = QPushButton()
        self.btn_export_bundle.setMinimumHeight(38)
        self.btn_export_bundle.clicked.connect(self._export_bundle)
        btn_bar.addWidget(self.btn_export_bundle)

        self.btn_factory_reset = QPushButton()
        self.btn_factory_reset.setObjectName("btn_warning")
        self.btn_factory_reset.setMinimumHeight(38)
        self.btn_factory_reset.clicked.connect(self._factory_reset)
        btn_bar.addWidget(self.btn_factory_reset)

        layout.addLayout(btn_bar)

        # Health Checks Table
        self.table_checks = QTableWidget()
        self.table_checks.setColumnCount(4)
        self.table_checks.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_checks.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_checks.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_checks.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_checks.setMaximumHeight(200)
        layout.addWidget(self.table_checks)

        # FAQ & Troubleshooting
        self.lbl_faq = QLabel()
        self.lbl_faq.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(self.lbl_faq)

        self.txt_faq = QTextBrowser()
        self.txt_faq.setStyleSheet("background-color: rgba(255, 255, 255, 0.02); padding: 10px; border-radius: 6px;")
        layout.addWidget(self.txt_faq)

        self._render_faq()

    def _render_faq(self):
        items = get_faq_items()
        html = ["<div style='font-family: sans-serif; font-size: 13px; line-height: 1.5;'>"]
        for idx, item in enumerate(items, 1):
            html.append(f"<p><b>{idx}. {item['q']}</b><br/><span style='color: #a6adc8;'>{item['a']}</span></p>")
        html.append("</div>")
        self.txt_faq.setHtml("".join(html))

    def _run_health_check(self):
        report: HealthReport = self.health_checker.run_all_checks()
        self.table_checks.setRowCount(len(report.checks))

        for row, check in enumerate(report.checks):
            item_name = QTableWidgetItem(check.name)
            item_status = QTableWidgetItem(check.status)
            if check.status == "PASS":
                item_status.setForeground(QColor("#a6e3a1"))
            elif check.status == "WARN":
                item_status.setForeground(QColor("#f9e2af"))
            else:
                item_status.setForeground(QColor("#f38ba8"))

            item_detail = QTableWidgetItem(check.detail)
            item_time = QTableWidgetItem(f"{check.duration_ms} ms")

            self.table_checks.setItem(row, 0, item_name)
            self.table_checks.setItem(row, 1, item_status)
            self.table_checks.setItem(row, 2, item_detail)
            self.table_checks.setItem(row, 3, item_time)

    def _export_bundle(self):
        try:
            zip_path = self.report_generator.generate_support_bundle()
            QMessageBox.information(
                self,
                "Support Bundle",
                tr("diag_bundle_created", path=str(zip_path))
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate support bundle: {e}")

    def _factory_reset(self):
        confirm = QMessageBox.warning(
            self,
            "Factory Reset",
            tr("settings_reset_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.recovery_manager.perform_factory_reset()
            QMessageBox.information(self, "Self-Recovery", "Configuration reset to default successfully. History was preserved.")

    def retranslate_ui(self):
        self.lbl_title.setText(tr("diag_title"))
        self.lbl_subtitle.setText(tr("diag_subtitle"))
        self.btn_run_check.setText(tr("diag_btn_run_check"))
        self.btn_export_bundle.setText(tr("diag_btn_export_bundle"))
        self.btn_factory_reset.setText(tr("diag_btn_factory_reset"))
        self.lbl_faq.setText(tr("diag_faq_title"))
        self.table_checks.setHorizontalHeaderLabels([
            "Check Item",
            "Status",
            "Details",
            "Duration"
        ])
