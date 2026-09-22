"""Unit tests for high-precision arithmetic operations."""

from decimal import Decimal
import pytest
from src.engine.decimal_math import (
    get_calculation_context,
    compute_sqrt,
    compute_divide,
    compute_power,
    compute_ln,
    compute_exp,
    compute_pi,
    compute_e,
    format_result
)
from src.engine.exceptions import (
    DivisionByZeroError,
    NegativeSqrtError,
    PrecisionOutOfRangeError,
    MathEngineError
)

def test_basic_arithmetic():
    ctx = get_calculation_context(50)
    a = Decimal("15.5")
    b = Decimal("2.75")
    assert ctx.add(a, b) == Decimal("18.25")
    assert ctx.subtract(a, b) == Decimal("12.75")
    assert ctx.multiply(a, Decimal("2")) == Decimal("31.0")
    assert compute_divide(Decimal("10"), Decimal("4"), ctx) == Decimal("2.5")

def test_division_by_zero():
    ctx = get_calculation_context(10)
    with pytest.raises(DivisionByZeroError):
        compute_divide(Decimal("10"), Decimal("0"), ctx)

def test_sqrt_positive_and_zero():
    ctx = get_calculation_context(10)
    assert compute_sqrt(Decimal("0"), ctx) == Decimal("0")
    assert compute_sqrt(Decimal("144"), ctx) == Decimal("12")
    assert compute_sqrt(Decimal("4"), ctx) == Decimal("2")

def test_sqrt_negative():
    ctx = get_calculation_context(10)
    with pytest.raises(NegativeSqrtError):
        compute_sqrt(Decimal("-25"), ctx)

def test_sqrt_2_high_precision_1000():
    # Known 100 first digits of sqrt(2)
    known_prefix = "1.4142135623730950488016887242096980785696718753769480731766797379907324784621070388503875343276415727"
    ctx = get_calculation_context(1000)
    val = compute_sqrt(Decimal(2), ctx)
    formatted = format_result(val, 1000)
    assert len(formatted.split('.')[1]) == 1000
    assert formatted.startswith(known_prefix)

def test_arbitrary_length_numbers_1000_digits():
    # Number with 1000 digits
    big_num_str = "9" * 1000
    big_num = Decimal(big_num_str)
    ctx = get_calculation_context(50)
    res = ctx.add(big_num, Decimal(1))
    assert str(res) == "1" + ("0" * 1000)

def test_power_operations():
    ctx = get_calculation_context(20)
    assert compute_power(Decimal(2), Decimal(10), ctx) == Decimal(1024)
    assert compute_power(Decimal(4), Decimal("0.5"), ctx) == Decimal(2)

    with pytest.raises(DivisionByZeroError):
        compute_power(Decimal(0), Decimal(-2), ctx)

    with pytest.raises(MathEngineError):
        compute_power(Decimal(-4), Decimal("0.5"), ctx)

def test_ln_and_exp():
    ctx = get_calculation_context(30)
    e_val = compute_e(30)
    ln_e = compute_ln(e_val, ctx)
    assert round(float(ln_e), 5) == 1.0

    exp_1 = compute_exp(Decimal(1), ctx)
    assert round(float(exp_1), 5) == round(float(e_val), 5)

    with pytest.raises(MathEngineError):
        compute_ln(Decimal(0), ctx)
    with pytest.raises(MathEngineError):
        compute_ln(Decimal(-5), ctx)

def test_pi_computation():
    pi_val = compute_pi(50)
    formatted = format_result(pi_val, 50)
    assert formatted.startswith("3.14159265358979323846264338327950288419716939937511")


def test_precision_bounds():
    with pytest.raises(PrecisionOutOfRangeError):
        get_calculation_context(-1)
    with pytest.raises(PrecisionOutOfRangeError):
        get_calculation_context(99999)

def test_format_result_rounding():
    val = Decimal("2.125")
    # Round half up
    assert format_result(val, 2) == "2.13"
    assert format_result(val, 0) == "2"
    assert format_result(val, 5) == "2.12500"
