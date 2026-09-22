"""Unit test verifying that keyboard input enters expression without clicking input field."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from src.ui.main_window import MainWindow

def test_keyboard_input_without_clicking_field(qapp):
    win = MainWindow()
    win.show()
    qapp.processEvents()

    calc = win.tab_calculator
    calc.slider_precision.setFocus()
    assert not calc.txt_expression.hasFocus()

    # Simulate keyboard typing
    for char in ["5", "*", "8", "+", "2"]:
        target = qapp.focusWidget() or win
        event = QKeyEvent(QKeyEvent.Type.KeyPress, 0, Qt.KeyboardModifier.NoModifier, char)
        qapp.sendEvent(target, event)
        qapp.processEvents()

    assert calc.txt_expression.text() == "5*8+2"

    # Press Enter to calculate
    target = qapp.focusWidget() or win
    enter_event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier, "\r")
    qapp.sendEvent(target, enter_event)
    qapp.processEvents()

    assert "42" in calc.txt_result.toPlainText()
    win.close()
