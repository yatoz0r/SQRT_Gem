"""Domain exceptions for the high-precision math engine."""

class MathEngineError(Exception):
    """Base exception for all mathematical evaluation errors."""
    def __init__(self, message: str, code: str = "GENERIC_ERROR", position: int = -1):
        super().__init__(message)
        self.message = message
        self.code = code
        self.position = position

class SyntaxMathError(MathEngineError):
    """Raised when mathematical expression syntax is invalid."""
    def __init__(self, detail: str, position: int = -1):
        super().__init__(f"Syntax error at position {position}: {detail}", code="SYNTAX_ERROR", position=position)
        self.detail = detail

class DivisionByZeroError(MathEngineError):
    """Raised when dividing by zero."""
    def __init__(self, position: int = -1):
        super().__init__("Division by zero", code="DIVISION_BY_ZERO", position=position)

class NegativeSqrtError(MathEngineError):
    """Raised when extracting square root of a negative real number."""
    def __init__(self, position: int = -1):
        super().__init__("Square root of a negative number", code="NEGATIVE_SQRT", position=position)

class UnknownIdentifierError(MathEngineError):
    """Raised when an identifier (function or constant) is unrecognized."""
    def __init__(self, name: str, position: int = -1):
        super().__init__(f"Unknown identifier '{name}'", code="UNKNOWN_IDENTIFIER", position=position)
        self.name = name

class MismatchedParenthesesError(MathEngineError):
    """Raised when opening/closing brackets do not balance."""
    def __init__(self, position: int = -1):
        super().__init__("Mismatched parentheses", code="MISMATCHED_PARENS", position=position)

class PrecisionOutOfRangeError(MathEngineError):
    """Raised when requested precision is negative or exceeds safe bounds."""
    def __init__(self, requested: int, max_allowed: int = 5000):
        super().__init__(f"Precision {requested} is out of valid range [0, {max_allowed}]", code="PRECISION_OUT_OF_RANGE")
        self.requested = requested
        self.max_allowed = max_allowed
