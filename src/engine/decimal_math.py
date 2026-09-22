"""High-precision mathematical computations using Python's decimal module."""

from decimal import Decimal, Context, localcontext, ROUND_HALF_UP, getcontext

from typing import Tuple
from src.engine.exceptions import (
    DivisionByZeroError,
    NegativeSqrtError,
    PrecisionOutOfRangeError,
    MathEngineError
)

# Number of guard digits added to internal calculations to prevent rounding artifacts
GUARD_DIGITS = 10
MAX_SUPPORTED_PRECISION = 2000

def get_calculation_context(precision: int, extra_digits: int = 0) -> Context:
    """Returns a Decimal Context configured for the given precision plus guard digits and large integer buffer."""
    if precision < 0 or precision > MAX_SUPPORTED_PRECISION:
        raise PrecisionOutOfRangeError(precision, MAX_SUPPORTED_PRECISION)
    # Total internal precision needs to accommodate numbers with >1000 integer digits, guard digits, and precision
    total_prec = max(2500, precision + extra_digits + GUARD_DIGITS + 50)
    return Context(prec=total_prec, rounding=ROUND_HALF_UP)


def compute_sqrt(value: Decimal, context: Context, position: int = -1) -> Decimal:
    """Computes square root with arbitrary precision."""
    if value < 0:
        raise NegativeSqrtError(position=position)
    if value == 0:
        return Decimal(0)
    return context.sqrt(value)

def compute_divide(a: Decimal, b: Decimal, context: Context, position: int = -1) -> Decimal:
    """Safely divides a by b with arbitrary precision."""
    if b == 0:
        raise DivisionByZeroError(position=position)
    return context.divide(a, b)

def compute_power(base: Decimal, exponent: Decimal, context: Context, position: int = -1) -> Decimal:
    """Computes base ** exponent with arbitrary precision."""
    if base == 0 and exponent < 0:
        raise DivisionByZeroError(position=position)
    if base < 0 and exponent != exponent.to_integral_value():
        raise MathEngineError("Fractional power of negative number is undefined in real numbers", code="FRACTIONAL_POWER_NEGATIVE", position=position)
    try:
        return context.power(base, exponent)
    except Exception as e:
        raise MathEngineError(f"Power computation failed: {str(e)}", code="POWER_ERROR", position=position)

def compute_ln(value: Decimal, context: Context, position: int = -1) -> Decimal:
    """Computes natural logarithm."""
    if value <= 0:
        raise MathEngineError("Natural logarithm is only defined for strictly positive numbers", code="NON_POSITIVE_LN", position=position)
    return context.ln(value)

def compute_exp(value: Decimal, context: Context, position: int = -1) -> Decimal:
    """Computes exponential function e^x."""
    return context.exp(value)

def compute_pi(precision: int) -> Decimal:
    """Computes pi to the specified precision using the Gauss-Legendre algorithm."""
    calc_prec = max(100, precision + GUARD_DIGITS + 30)
    ctx = Context(prec=calc_prec, rounding=ROUND_HALF_UP)
    with localcontext(ctx):
        one = Decimal(1)
        two = Decimal(2)
        four = Decimal(4)
        
        a = one
        b = one / two.sqrt()
        t = one / four
        p = one
        
        # 12 iterations provide over 1500 digits of accuracy
        iterations = 12 if precision <= 1000 else 16
        for _ in range(iterations):
            a_next = (a + b) / two
            b = (a * b).sqrt()
            t -= p * ((a - a_next) ** 2)
            a = a_next
            p = two * p
            
        return ((a + b) ** 2) / (four * t)

def compute_e(precision: int) -> Decimal:
    """Computes Euler's constant e using C-accelerated Decimal.exp()."""
    calc_prec = max(100, precision + GUARD_DIGITS + 30)
    ctx = Context(prec=calc_prec, rounding=ROUND_HALF_UP)
    with localcontext(ctx):
        return ctx.exp(Decimal(1))


def format_result(value: Decimal, precision: int) -> str:
    """
    Formats the decimal result according to the requested decimal places.
    Trailing zeros after decimal point are preserved according to exact requested precision,
    or truncated cleanly if precision is 0.
    """
    int_digits = max(1, abs(value.adjusted()) + 10) if value != 0 else 1
    ctx = get_calculation_context(precision, extra_digits=int_digits)
    if precision == 0:
        rounded = value.quantize(Decimal('1'), rounding=ROUND_HALF_UP, context=ctx)
        return str(rounded)
    
    pattern = '0.' + ('0' * precision)
    rounded = value.quantize(Decimal(pattern), rounding=ROUND_HALF_UP, context=ctx)
    return f"{rounded:f}"


