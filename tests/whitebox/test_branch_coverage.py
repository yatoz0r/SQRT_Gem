"""White-box testing targeting full branch coverage for parser and mathematical evaluation."""

import pytest
from decimal import Decimal
from src.engine import MathEngine
from src.engine.lexer import Lexer, TokenType
from src.engine.parser import Parser
from src.engine.decimal_math import get_calculation_context, compute_divide, compute_power, compute_sqrt
from src.engine.exceptions import (
    SyntaxMathError,
    DivisionByZeroError,
    NegativeSqrtError,
    MismatchedParenthesesError,
    UnknownIdentifierError
)

def test_lexer_edge_branches():
    # Test whitespaces, operators, decimals
    tokens = Lexer("  + - * / ^ ( ) , abs ln exp sqrt  ").tokenize()
    assert tokens[-1].type == TokenType.EOF

    # Test single dot error
    with pytest.raises(SyntaxMathError) as exc:
        Lexer(" . ").tokenize()
    assert "not a valid number" in str(exc.value)

    # Test unknown character
    with pytest.raises(SyntaxMathError) as exc:
        Lexer(" 5 # 3 ").tokenize()
    assert "Unexpected character" in str(exc.value)

def test_parser_unary_and_binary_branches():
    engine = MathEngine()

    # Unary plus
    res = engine.evaluate("+5 + +10", precision=2)
    assert res.formatted_value == "15.00"

    # Consecutive unary minuses: -(-5)
    res = engine.evaluate("-(-5)", precision=2)
    assert res.formatted_value == "5.00"

    # Power associativity: 2^3^2 = 2^(3^2) = 2^9 = 512
    res = engine.evaluate("2^3^2", precision=0)
    assert res.formatted_value == "512"

    # Multiple function arguments syntax error (e.g. sqrt(1, 2))
    with pytest.raises(SyntaxMathError) as exc:
        engine.evaluate("sqrt(1, 2)")
    assert "takes exactly 1 argument" in str(exc.value)

    # Abs function with multiple args
    with pytest.raises(SyntaxMathError) as exc:
        engine.evaluate("abs(1, 2)")
    assert "takes exactly 1 argument" in str(exc.value)

    # Ln with invalid args count
    with pytest.raises(SyntaxMathError) as exc:
        engine.evaluate("ln(1, 2)")
    assert "takes exactly 1 argument" in str(exc.value)

    # Exp with invalid args count
    with pytest.raises(SyntaxMathError) as exc:
        engine.evaluate("exp(1, 2)")
    assert "takes exactly 1 argument" in str(exc.value)

def test_parser_unexpected_trailing_token():
    with pytest.raises(SyntaxMathError):
        Parser(Lexer("5 5").tokenize()).parse()

def test_decimal_math_branches():
    ctx = get_calculation_context(10)

    # Sqrt zero
    assert compute_sqrt(Decimal(0), ctx) == Decimal(0)

    # Divide
    assert compute_divide(Decimal(10), Decimal(2), ctx) == Decimal(5)

    # Power 0^(-1)
    with pytest.raises(DivisionByZeroError):
        compute_power(Decimal(0), Decimal(-1), ctx)

    # Power negative base with non-integer exponent
    with pytest.raises(Exception):
        compute_power(Decimal(-2), Decimal("0.333"), ctx)
