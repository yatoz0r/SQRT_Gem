"""Unit tests for MathEngine evaluation and analytical expressions."""

import pytest
from decimal import Decimal
from src.engine import MathEngine, CalculationResult
from src.engine.exceptions import (
    DivisionByZeroError,
    NegativeSqrtError,
    SyntaxMathError,
    UnknownIdentifierError
)

def test_evaluator_basic_operations(math_engine):
    res = math_engine.evaluate("10 + 5 * 2", precision=2)
    assert res.formatted_value == "20.00"

    res = math_engine.evaluate("(15.5 + 2.75) * sqrt(144)", precision=2)
    assert res.formatted_value == "219.00"

def test_evaluator_division_by_zero(math_engine):
    with pytest.raises(DivisionByZeroError):
        math_engine.evaluate("10 / 0")

    with pytest.raises(DivisionByZeroError):
        math_engine.evaluate("15 / (5 - 5)")

def test_evaluator_negative_sqrt(math_engine):
    with pytest.raises(NegativeSqrtError):
        math_engine.evaluate("sqrt(-100)")

def test_evaluator_nested_functions(math_engine):
    res = math_engine.evaluate("sqrt(abs(-64))", precision=0)
    assert res.formatted_value == "8"

def test_evaluator_constants(math_engine):
    res = math_engine.evaluate("pi * 2", precision=10)
    assert res.formatted_value == "6.2831853072"

    res = math_engine.evaluate("e + 1", precision=5)
    assert res.formatted_value.startswith("3.71828")

def test_evaluator_unknown_identifier(math_engine):
    with pytest.raises(UnknownIdentifierError):
        math_engine.evaluate("unknownFunc(5)")

def test_evaluator_large_numbers(math_engine):
    expr = "123456789012345678901234567890 / 987654321"
    res = math_engine.evaluate(expr, precision=10)
    assert res.formatted_value.startswith("124999998873437499901.5820312399")


def test_evaluator_empty_string(math_engine):
    with pytest.raises(SyntaxMathError):
        math_engine.evaluate("   ")
