"""History Tab for inspecting, filtering, reusing, and exporting past calculations."""

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QHeaderView, QFileDialog, QMessageBox, QApplication
)
from src.storage import HistoryManager, HistoryRecord
from src.i18n import tr

class HistoryTab(QWidget):
    """Tab displaying persistent history of calculations with export capabilities."""

    reuse_requested = Signal(str, int)  # Emits (expression, precision)

    def __init__(self, history_manager: HistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager

        self._init_ui()
        self.refresh_table()
        self.retranslate_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Top Bar: Search and Actions
        top_bar = QHBoxLayout()
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Search in history...")
        self.txt_filter.setClearButtonEnabled(True)
        self.txt_filter.textChanged.connect(self._filter_table)
        top_bar.addWidget(self.txt_filter)

        self.btn_export_csv = QPushButton()
        self.btn_export_csv.clicked.connect(self._export_csv)
        top_bar.addWidget(self.btn_export_csv)

        self.btn_export_json = QPushButton()
        self.btn_export_json.clicked.connect(self._export_json)
        top_bar.addWidget(self.btn_export_json)

        self.btn_clear_all = QPushButton()
        self.btn_clear_all.clicked.connect(self._clear_all)
        top_bar.addWidget(self.btn_clear_all)

        layout.addLayout(top_bar)

        # History Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Bottom Action Buttons
        bottom_bar = QHBoxLayout()
        self.btn_reuse = QPushButton()
        self.btn_reuse.setObjectName("btn_primary")
        self.btn_reuse.clicked.connect(self._reuse_selected)
        bottom_bar.addWidget(self.btn_reuse)

        self.btn_copy = QPushButton()
        self.btn_copy.clicked.connect(self._copy_selected)
        bottom_bar.addWidget(self.btn_copy)

        self.btn_delete = QPushButton()
        self.btn_delete.clicked.connect(self._delete_selected)
        bottom_bar.addWidget(self.btn_delete)

        bottom_bar.addStretch()
        self.lbl_count = QLabel()
        bottom_bar.addWidget(self.lbl_count)

        layout.addLayout(bottom_bar)

    def refresh_table(self):
        records = self.history_manager.get_records()
        self.table.setRowCount(len(records))

        for row, rec in enumerate(records):
            item_time = QTableWidgetItem(rec.timestamp)
            item_time.setData(Qt.ItemDataRole.UserRole, rec.id)

            item_expr = QTableWidgetItem(rec.expression)
            item_prec = QTableWidgetItem(str(rec.precision))
            item_res = QTableWidgetItem(rec.result)

            self.table.setItem(row, 0, item_time)
            self.table.setItem(row, 1, item_expr)
            self.table.setItem(row, 2, item_prec)
            self.table.setItem(row, 3, item_res)

        self.lbl_count.setText(f"Total: {len(records)}")

    def _filter_table(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            expr_item = self.table.item(row, 1)
            res_item = self.table.item(row, 3)
            match = False
            if expr_item and query in expr_item.text().lower():
                match = True
            elif res_item and query in res_item.text().lower():
                match = True
            self.table.setRowHidden(row, not match if query else False)

    def _get_selected_record(self) -> tuple:
        selected = self.table.currentRow()
        if selected < 0:
            return None, None, None, None
        rec_id = self.table.item(selected, 0).data(Qt.ItemDataRole.UserRole)
        expr = self.table.item(selected, 1).text()
        prec = int(self.table.item(selected, 2).text())
        res = self.table.item(selected, 3).text()
        return rec_id, expr, prec, res

    def _reuse_selected(self):
        rec_id, expr, prec, _ = self._get_selected_record()
        if expr:
            self.reuse_requested.emit(expr, prec)

    def _copy_selected(self):
        _, _, _, res = self._get_selected_record()
        if res:
            QApplication.clipboard().setText(res)

    def _delete_selected(self):
        rec_id, _, _, _ = self._get_selected_record()
        if rec_id:
            self.history_manager.delete_record(rec_id)
            self.refresh_table()

    def _clear_all(self):
        if self.table.rowCount() == 0:
            return
        confirm = QMessageBox.question(
            self,
            tr("history_clear_all"),
            "Clear all calculation history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.history_manager.clear()
            self.refresh_table()

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, tr("history_export_csv"), "history.csv", "CSV Files (*.csv)")
        if path:
            self.history_manager.export_to_csv(Path(path))
            QMessageBox.information(self, "Export", tr("history_exported_success", path=path))

    def _export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, tr("history_export_json"), "history.json", "JSON Files (*.json)")
        if path:
            self.history_manager.export_to_json(Path(path))
            QMessageBox.information(self, "Export", tr("history_exported_success", path=path))

    def retranslate_ui(self):
        self.table.setHorizontalHeaderLabels([
            tr("history_time"),
            tr("history_expression"),
            tr("history_precision"),
            tr("history_result")
        ])
        self.btn_reuse.setText(tr("history_reuse"))
        self.btn_copy.setText(tr("history_copy"))
        self.btn_delete.setText(tr("history_delete"))
        self.btn_clear_all.setText(tr("history_clear_all"))
        self.btn_export_csv.setText(tr("history_export_csv"))
        self.btn_export_json.setText(tr("history_export_json"))
