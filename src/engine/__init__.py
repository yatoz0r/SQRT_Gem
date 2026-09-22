"""High-precision mathematical engine package."""

from src.engine.evaluator import MathEngine, CalculationResult
from src.engine.exceptions import (
    MathEngineError,
    SyntaxMathError,
    DivisionByZeroError,
    NegativeSqrtError,
    UnknownIdentifierError,
    MismatchedParenthesesError,
    PrecisionOutOfRangeError
)

__all__ = [
    "MathEngine",
    "CalculationResult",
    "MathEngineError",
    "SyntaxMathError",
    "DivisionByZeroError",
    "NegativeSqrtError",
    "UnknownIdentifierError",
    "MismatchedParenthesesError",
    "PrecisionOutOfRangeError"
]
