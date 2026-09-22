"""Polished Modal Update Dialog with progress tracking, changelog, and integrity verification."""

from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextBrowser, QFrame, QMessageBox
)
from src.updater.models import UpdateInfo
from src.updater.download_manager import DownloadManager, DownloadWorker
from src.updater.installer_runner import InstallerRunner
from src.i18n import tr

class UpdateDialog(QDialog):
    """Modal dialog displaying update information, changelog, and download progress."""

    def __init__(self, parent=None, update_info: Optional[UpdateInfo] = None):
        super().__init__(parent)
        self.update_info = update_info
        self.download_manager = DownloadManager()
        self.download_thread: Optional[QThread] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.downloaded_installer_path: Optional[str] = None

        self._init_ui()
        self._populate_data()

    def _init_ui(self):
        self.setWindowTitle(tr("update_title"))
        self.setFixedSize(540, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header: Version comparison and Type Badge
        header_layout = QHBoxLayout()
        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.lbl_badge = QLabel()
        self.lbl_badge.setStyleSheet(
            "padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold;"
        )
        header_layout.addWidget(self.lbl_badge)
        layout.addLayout(header_layout)

        # Release Date
        self.lbl_date = QLabel()
        self.lbl_date.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self.lbl_date)

        # Critical Alert Banner (if critical)
        self.banner_frame = QFrame()
        self.banner_frame.setStyleSheet(
            "background-color: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); "
            "border-radius: 8px; padding: 10px;"
        )
        banner_layout = QHBoxLayout(self.banner_frame)
        banner_layout.setContentsMargins(8, 6, 8, 6)
        self.lbl_banner = QLabel(tr("update_critical_warning"))
        self.lbl_banner.setWordWrap(True)
        self.lbl_banner.setStyleSheet("color: #f87171; font-weight: 500; font-size: 12px;")
        banner_layout.addWidget(self.lbl_banner)
        layout.addWidget(self.banner_frame)
        self.banner_frame.hide()

        # Changelog
        lbl_changelog_title = QLabel(tr("update_changelog"))
        lbl_changelog_title.setStyleSheet("font-weight: 600; font-size: 13px; margin-top: 4px;")
        layout.addWidget(lbl_changelog_title)

        self.txt_changelog = QTextBrowser()
        self.txt_changelog.setOpenExternalLinks(True)
        self.txt_changelog.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); "
            "border-radius: 8px; padding: 10px; font-size: 13px; line-height: 1.4;"
        )
        layout.addWidget(self.txt_changelog)

        # Progress Section (hidden initially)
        self.progress_container = QFrame()
        p_layout = QVBoxLayout(self.progress_container)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background-color: rgba(255, 255, 255, 0.05); border-radius: 6px; height: 16px; text-align: center; } "
            "QProgressBar::chunk { background-color: #6366f1; border-radius: 6px; }"
        )
        p_layout.addWidget(self.progress_bar)

        self.lbl_progress_status = QLabel("")
        self.lbl_progress_status.setStyleSheet("color: #94a3b8; font-size: 11px;")
        p_layout.addWidget(self.lbl_progress_status)
        layout.addWidget(self.progress_container)
        self.progress_container.hide()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_later = QPushButton(tr("update_btn_later"))
        self.btn_later.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_later)

        self.btn_action = QPushButton(tr("update_btn_install"))
        self.btn_action.setObjectName("btn_primary")
        self.btn_action.setStyleSheet("padding: 8px 18px; font-weight: 600;")
        self.btn_action.clicked.connect(self._on_action_clicked)
        btn_layout.addWidget(self.btn_action)

        layout.addLayout(btn_layout)

    def _populate_data(self):
        if not self.update_info:
            return

        info = self.update_info
        self.lbl_title.setText(f"v{info.current_version}  →  v{info.latest_version}")

        # Badge styling
        if info.is_critical:
            self.lbl_badge.setText(tr("update_badge_critical"))
            self.lbl_badge.setStyleSheet(
                "background-color: rgba(239, 68, 68, 0.2); color: #f87171; "
                "border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px; padding: 4px 8px;"
            )
            self.banner_frame.show()
        elif info.update_type == "patch":
            self.lbl_badge.setText(tr("update_badge_patch"))
            self.lbl_badge.setStyleSheet(
                "background-color: rgba(16, 185, 129, 0.2); color: #34d399; "
                "border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 6px; padding: 4px 8px;"
            )
        else:
            self.lbl_badge.setText(tr("update_badge_feature"))
            self.lbl_badge.setStyleSheet(
                "background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; "
                "border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 6px; padding: 4px 8px;"
            )

        if info.release_date:
            self.lbl_date.setText(f"Release: {info.release_date}")
        else:
            self.lbl_date.hide()

        # Format changelog
        cl_text = info.changelog or "No changelog provided."
        self.txt_changelog.setPlainText(cl_text)

    def _on_action_clicked(self):
        if self.downloaded_installer_path:
            # Install & Restart
            InstallerRunner.launch(self.downloaded_installer_path, passive=True, quit_app=True)
            self.accept()
            return

        if self.btn_action.text() == tr("update_btn_cancel"):
            # Cancel download
            if self.download_manager:
                self.download_manager.cancel()
            return

        # Start download
        self._start_download()

    def _start_download(self):
        asset = self.update_info.get_platform_asset()
        url = asset.download_url if asset else self.update_info.download_url
        sha256 = asset.sha256 if asset else self.update_info.sha256
        filename = asset.filename if asset else None

        if not url:
            QMessageBox.warning(self, tr("update_title"), "No download URL available for this platform.")
            return

        self.progress_container.show()
        self.progress_bar.setValue(0)
        self.lbl_progress_status.setText(tr("update_downloading"))
        self.btn_later.setEnabled(False)
        self.btn_action.setText(tr("update_btn_cancel"))

        self.download_thread = QThread()
        self.download_worker = DownloadWorker(
            manager=self.download_manager,
            url=url,
            expected_sha256=sha256,
            filename=filename
        )
        self.download_worker.moveToThread(self.download_thread)

        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.progress_updated.connect(self._on_download_progress)
        self.download_worker.download_finished.connect(self._on_download_finished)
        self.download_worker.download_error.connect(self._on_download_error)
        self.download_worker.download_cancelled.connect(self._on_download_cancelled)

        self.download_worker.download_finished.connect(self.download_thread.quit)
        self.download_worker.download_error.connect(self.download_thread.quit)
        self.download_worker.download_cancelled.connect(self.download_thread.quit)

        self.download_thread.start()

    def _on_download_progress(self, bytes_read: int, total_bytes: int, percent: float, speed_bps: float):
        self.progress_bar.setValue(int(percent))
        mb_read = bytes_read / (1024 * 1024)
        mb_total = total_bytes / (1024 * 1024)
        speed_kb = speed_bps / 1024
        if speed_kb > 1024:
            speed_str = f"{speed_kb / 1024:.2f} MB/s"
        else:
            speed_str = f"{speed_kb:.0f} KB/s"

        if total_bytes > 0:
            status_text = f"{mb_read:.1f} MB / {mb_total:.1f} MB ({speed_str})"
        else:
            status_text = f"{mb_read:.1f} MB ({speed_str})"
        self.lbl_progress_status.setText(status_text)

    def _on_download_finished(self, file_path: str):
        self.downloaded_installer_path = file_path
        self.progress_bar.setValue(100)
        self.lbl_progress_status.setText(tr("update_ready"))
        self.btn_action.setText(tr("update_btn_install_now"))
        self.btn_later.setEnabled(True)

    def _on_download_error(self, err_msg: str):
        self.progress_container.hide()
        self.btn_later.setEnabled(True)
        self.btn_action.setText(tr("update_btn_retry"))

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(tr("update_title"))
        msg_box.setText(tr("update_download_error", error=err_msg))

        btn_browser = None
        target_url = (self.update_info.download_url if self.update_info else "") or "https://github.com/yatoz0r/SQRT_Gem/releases"
        if target_url:
            btn_browser = msg_box.addButton("GitHub Releases", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        if btn_browser and msg_box.clickedButton() == btn_browser:
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl(target_url))

    def _on_download_cancelled(self):
        self.progress_container.hide()
        self.btn_later.setEnabled(True)
        self.btn_action.setText(tr("update_btn_install"))

    def closeEvent(self, event):
        if self.download_manager:
            self.download_manager.cancel()
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.quit()
            self.download_thread.wait(1000)
        super().closeEvent(event)
