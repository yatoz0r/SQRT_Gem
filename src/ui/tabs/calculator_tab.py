"""Calculator Tab for high-precision analytical calculations."""

import traceback
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel,
    QSpinBox, QSlider, QFrame, QSizePolicy, QApplication
)
from src.engine import MathEngine, CalculationResult, MathEngineError, SyntaxMathError
from src.storage import HistoryManager
from src.i18n import tr

class CalculatorTab(QWidget):
    """Primary tab providing mathematical expression input, precision control, and result inspection."""

    calculation_completed = Signal(object)  # Emits CalculationResult

    def __init__(self, history_manager: HistoryManager, default_precision: int = 50, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.engine = MathEngine()
        self.default_precision = default_precision

        self._init_ui()
        self.retranslate_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # 1. Expression Input Section
        input_layout = QVBoxLayout()
        self.lbl_input = QLabel()
        self.lbl_input.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(self.lbl_input)

        expr_row = QHBoxLayout()
        self.txt_expression = QLineEdit()
        self.txt_expression.setClearButtonEnabled(True)
        self.txt_expression.setStyleSheet("font-size: 15px; font-family: monospace; padding: 8px;")
        self.txt_expression.returnPressed.connect(self.calculate)
        expr_row.addWidget(self.txt_expression)

        self.btn_clear = QPushButton()
        self.btn_clear.clicked.connect(self.clear_input)
        expr_row.addWidget(self.btn_clear)

        self.btn_calc = QPushButton()
        self.btn_calc.setObjectName("btn_primary")
        self.btn_calc.clicked.connect(self.calculate)
        expr_row.addWidget(self.btn_calc)

        input_layout.addLayout(expr_row)
        main_layout.addLayout(input_layout)

        # 2. Precision Controls Section
        prec_frame = QFrame()
        prec_frame.setObjectName("surface_card")
        prec_layout = QHBoxLayout(prec_frame)

        self.lbl_precision = QLabel()
        prec_layout.addWidget(self.lbl_precision)

        self.slider_precision = QSlider(Qt.Orientation.Horizontal)
        self.slider_precision.setRange(0, 1000)
        self.slider_precision.setValue(self.default_precision)
        prec_layout.addWidget(self.slider_precision)

        self.spin_precision = QSpinBox()
        self.spin_precision.setRange(0, 1000)
        self.spin_precision.setValue(self.default_precision)
        prec_layout.addWidget(self.spin_precision)

        self.slider_precision.valueChanged.connect(self.spin_precision.setValue)
        self.spin_precision.valueChanged.connect(self.slider_precision.setValue)

        main_layout.addWidget(prec_frame)

        # 3. Quick Keypad
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(6)
        buttons = [
            ("sqrt(", 0, 0), ("^", 0, 1), ("(", 0, 2), (")", 0, 3), ("/", 0, 4),
            ("abs(", 1, 0), ("ln(", 1, 1), ("pi", 1, 2), ("e", 1, 3), ("*", 1, 4),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("-", 2, 3), ("+", 2, 4),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("0", 3, 3), (".", 3, 4),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("C", 4, 3), ("=", 4, 4)
        ]

        numbers = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."}
        ops = {"+", "-", "*", "/", "^", "(", ")"}
        funcs = {"sqrt(", "abs(", "ln(", "exp(", "pi", "e"}

        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(36)

            if text in numbers:
                btn.setObjectName("btn_num")
            elif text in ops:
                btn.setObjectName("btn_op")
            elif text in funcs:
                btn.setObjectName("btn_func")
            elif text == "C":
                btn.setObjectName("btn_clear")
            elif text == "=":
                btn.setObjectName("btn_equals")

            if text == "=":
                btn.clicked.connect(self.calculate)
            elif text == "C":
                btn.clicked.connect(self.clear_input)
            else:
                btn.clicked.connect(lambda _, t=text: self._append_to_expression(t))
            keypad_layout.addWidget(btn, row, col)

        for r in range(5):
            keypad_layout.setRowStretch(r, 1)
        for c in range(5):
            keypad_layout.setColumnStretch(c, 1)

        main_layout.addLayout(keypad_layout)

        # 4. Error Banner Section (Hidden by default)
        self.error_frame = QFrame()
        self.error_frame.setStyleSheet("background-color: #3b181e; border: 1px solid #f38ba8; border-radius: 8px; padding: 8px;")
        self.error_frame.setVisible(False)
        error_layout = QVBoxLayout(self.error_frame)

        self.lbl_error_message = QLabel()
        self.lbl_error_message.setStyleSheet("color: #f38ba8; font-weight: bold; font-size: 13px;")
        self.lbl_error_message.setWordWrap(True)
        error_layout.addWidget(self.lbl_error_message)

        self.txt_error_details = QTextEdit()
        self.txt_error_details.setReadOnly(True)
        self.txt_error_details.setMaximumHeight(80)
        self.txt_error_details.setStyleSheet("background-color: #181825; color: #a6adc8; font-family: monospace; font-size: 11px;")
        self.txt_error_details.setVisible(False)
        error_layout.addWidget(self.txt_error_details)

        self.btn_toggle_error_details = QPushButton()
        self.btn_toggle_error_details.setFlat(True)
        self.btn_toggle_error_details.setStyleSheet("color: #89b4fa; text-align: left; font-size: 11px;")
        self.btn_toggle_error_details.clicked.connect(self._toggle_error_details)
        error_layout.addWidget(self.btn_toggle_error_details)

        main_layout.addWidget(self.error_frame)

        # 5. Result Display Section
        result_header = QHBoxLayout()
        self.lbl_result_title = QLabel()
        self.lbl_result_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        result_header.addWidget(self.lbl_result_title)

        result_header.addStretch()
        self.lbl_metrics = QLabel()
        self.lbl_metrics.setStyleSheet("color: #94a3b8; font-size: 12px;")
        result_header.addWidget(self.lbl_metrics)

        self.btn_copy = QPushButton()
        self.btn_copy.clicked.connect(self.copy_result)
        result_header.addWidget(self.btn_copy)

        main_layout.addLayout(result_header)

        self.txt_result = QTextEdit()
        self.txt_result.setObjectName("result_display")
        self.txt_result.setReadOnly(True)
        self.txt_result.setMinimumHeight(130)
        main_layout.addWidget(self.txt_result)

    def _append_to_expression(self, text: str):
        current = self.txt_expression.text()
        cursor_pos = self.txt_expression.cursorPosition()
        new_text = current[:cursor_pos] + text + current[cursor_pos:]
        self.txt_expression.setText(new_text)
        self.txt_expression.setCursorPosition(cursor_pos + len(text))
        self.txt_expression.setFocus()

    def clear_input(self):
        self.txt_expression.clear()
        self.error_frame.setVisible(False)
        self.txt_expression.setFocus()

    def calculate(self):
        expr = self.txt_expression.text().strip()
        if not expr:
            return

        precision = self.spin_precision.value()
        self.error_frame.setVisible(False)

        try:
            result: CalculationResult = self.engine.evaluate(expr, precision=precision)
            self.txt_result.setText(result.formatted_value)

            # Update metrics
            time_txt = tr("label_calc_time", time=result.elapsed_ms)
            digits_txt = tr("label_digits_count", count=result.digits_count)
            self.lbl_metrics.setText(f"{digits_txt}  |  {time_txt}")

            # Save to history
            self.history_manager.add_record(
                expression=expr,
                precision=precision,
                result=result.formatted_value,
                execution_time_ms=result.elapsed_ms
            )

            self.calculation_completed.emit(result)

        except MathEngineError as e:
            self._show_error(e)
        except Exception as e:
            self._show_unexpected_error(e)

    def _show_error(self, err: MathEngineError):
        self.txt_result.clear()
        self.lbl_metrics.setText("")

        # Localize specific known errors
        if err.code == "DIVISION_BY_ZERO":
            msg = tr("err_division_by_zero")
        elif err.code == "NEGATIVE_SQRT":
            msg = tr("err_negative_sqrt")
        elif err.code == "SYNTAX_ERROR":
            msg = tr("err_syntax", pos=err.position, detail=getattr(err, 'detail', str(err)))
        elif err.code == "MISMATCHED_PARENS":
            msg = tr("err_mismatched_parens")
        elif err.code == "UNKNOWN_IDENTIFIER":
            msg = tr("err_unknown_func", name=getattr(err, 'name', ''))
        elif err.code == "PRECISION_OUT_OF_RANGE":
            msg = tr("err_precision_out_of_range", max=1000)
        else:
            msg = err.message

        self.lbl_error_message.setText(msg)
        details = f"ErrorCode: {err.code}\nPosition: {err.position}\nException: {type(err).__name__}: {str(err)}"
        self.txt_error_details.setText(details)
        self.error_frame.setVisible(True)

    def _show_unexpected_error(self, exc: Exception):
        self.txt_result.clear()
        self.lbl_metrics.setText("")
        self.lbl_error_message.setText(f"System Error: {str(exc)}")
        self.txt_error_details.setText(traceback.format_exc())
        self.error_frame.setVisible(True)

    def _toggle_error_details(self):
        self.txt_error_details.setVisible(not self.txt_error_details.isVisible())

    def copy_result(self):
        text = self.txt_result.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            prev_metrics = self.lbl_metrics.text()
            self.lbl_metrics.setText(tr("copied_notification"))
            # restore after a moment

    def set_expression(self, expression: str, precision: int = None):
        """Used when reusing expression from history."""
        self.txt_expression.setText(expression)
        if precision is not None:
            self.spin_precision.setValue(precision)
        self.txt_expression.setFocus()

    def retranslate_ui(self):
        self.lbl_input.setText(tr("tab_calculator"))
        self.txt_expression.setPlaceholderText(tr("input_placeholder"))
        self.btn_clear.setText(tr("btn_clear"))
        self.btn_calc.setText(tr("btn_calculate"))
        self.lbl_precision.setText(tr("label_precision"))
        self.lbl_result_title.setText(tr("label_result"))
        self.btn_copy.setText(tr("btn_copy"))
        self.btn_toggle_error_details.setText(tr("error_details"))
