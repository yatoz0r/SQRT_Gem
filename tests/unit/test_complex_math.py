"""Unit tests for arbitrary precision complex arithmetic and evaluator integration.

Validates Section 1 of TZ_dopolnenie.md:
'1. Функциональность: комплексные длинные числа, заданная точность, аналитические выражения, текстовый ввод'
"""

import pytest
from decimal import Decimal
from src.engine.complex_math import DecimalComplex
from src.engine.evaluator import MathEngine
from src.engine.decimal_math import get_calculation_context
from src.engine.exceptions import DivisionByZeroError, NegativeSqrtError

@pytest.fixture
def engine():
    return MathEngine()

@pytest.fixture
def ctx():
    return get_calculation_context(50)

def test_complex_basic_arithmetic(ctx):
    z1 = DecimalComplex(Decimal("2"), Decimal("3"))
    z2 = DecimalComplex(Decimal("1"), Decimal("-2"))

    # Addition
    res_add = z1.add(z2, ctx)
    assert res_add.real == Decimal("3")
    assert res_add.imag == Decimal("1")

    # Subtraction
    res_sub = z1.subtract(z2, ctx)
    assert res_sub.real == Decimal("1")
    assert res_sub.imag == Decimal("5")

    # Multiplication: (2 + 3i)(1 - 2i) = 2 - 4i + 3i - 6(-1) = 8 - i
    res_mul = z1.multiply(z2, ctx)
    assert res_mul.real == Decimal("8")
    assert res_mul.imag == Decimal("-1")

    # Division: (1 + i) / (1 - i) = (1+i)^2 / 2 = 2i / 2 = i
    c1 = DecimalComplex(Decimal("1"), Decimal("1"))
    c2 = DecimalComplex(Decimal("1"), Decimal("-1"))
    res_div = c1.divide(c2, ctx)
    assert res_div.real == Decimal("0")
    assert res_div.imag == Decimal("1")

def test_complex_division_by_zero(ctx):
    z1 = DecimalComplex(Decimal("5"), Decimal("5"))
    z_zero = DecimalComplex(Decimal("0"), Decimal("0"))
    with pytest.raises(DivisionByZeroError):
        z1.divide(z_zero, ctx)

def test_complex_powers_and_i_cycle(ctx):
    i = DecimalComplex(Decimal("0"), Decimal("1"))
    # i^0 = 1
    assert i.power(DecimalComplex(0, 0), ctx).real == Decimal("1")
    # i^1 = i
    assert i.power(DecimalComplex(1, 0), ctx).imag == Decimal("1")
    # i^2 = -1
    assert i.power(DecimalComplex(2, 0), ctx).real == Decimal("-1")
    # i^3 = -i
    assert i.power(DecimalComplex(3, 0), ctx).imag == Decimal("-1")
    # i^4 = 1
    assert i.power(DecimalComplex(4, 0), ctx).real == Decimal("1")

def test_complex_sqrt(ctx):
    # sqrt(-144) = 12i
    neg = DecimalComplex(Decimal("-144"), Decimal("0"))
    res = neg.sqrt(ctx)
    assert res.real == Decimal("0")
    assert res.imag == Decimal("12")

    # sqrt(3 + 4i) = 2 + i (since (2+i)^2 = 4 + 4i - 1 = 3 + 4i)
    z = DecimalComplex(Decimal("3"), Decimal("4"))
    res_z = z.sqrt(ctx)
    assert res_z.real == Decimal("2")
    assert res_z.imag == Decimal("1")

def test_evaluator_complex_expressions(engine):
    # Expressions using imaginary unit 'i'
    r1 = engine.evaluate("2 + 3*i + 4 - 5*i", precision=2)
    assert r1.is_complex is True
    assert "6.00 - 2.00i" in r1.formatted_value


    # (2 + 3*i) * (2 - 3*i) = 4 - 9*(-1) = 13 (pure real)
    r2 = engine.evaluate("(2 + 3*i) * (2 - 3*i)", precision=2)
    assert r2.is_complex is False
    assert r2.formatted_value == "13.00"

    # i^2 = -1
    r3 = engine.evaluate("i ^ 2", precision=2)
    assert r3.is_complex is False
    assert r3.formatted_value == "-1.00"

    # Explicit allow_complex on sqrt(-100)
    r4 = engine.evaluate("sqrt(-100)", precision=2, allow_complex=True)
    assert r4.is_complex is True
    assert "10.00i" in r4.formatted_value

def test_complex_large_numbers_1000_digits(engine):
    # Arbitrary precision with large 1000-digit complex numbers
    large_num = "9" * 1000
    expr = f"({large_num} + {large_num}*i) - ({large_num} + {large_num}*i)"
    res = engine.evaluate(expr, precision=2)
    assert res.formatted_value == "0.00"
    assert res.is_complex is False

def test_complex_formatting():
    z_pure_i = DecimalComplex(0, 1)
    assert z_pure_i.format(2) == "i"

    z_neg_i = DecimalComplex(0, -1)
    assert z_neg_i.format(2) == "-i"

    z_both = DecimalComplex(Decimal("2.5"), Decimal("-3.5"))
    assert z_both.format(2) == "2.50 - 3.50i"

    z_real = DecimalComplex(Decimal("5"), Decimal("0"))
    assert repr(z_real) == "DecimalComplex(5)"

    z_comp = DecimalComplex(Decimal("5"), Decimal("2"))
    assert repr(z_comp) == "DecimalComplex(5 + 2i)"

def test_complex_power_edge_cases(ctx):
    # 0^positive = 0
    zero = DecimalComplex(0, 0)
    assert zero.power(DecimalComplex(2, 0), ctx).real == Decimal(0)

    # 0^non-positive raises DivisionByZero
    with pytest.raises(DivisionByZeroError):
        zero.power(DecimalComplex(-1, 0), ctx)

    # Negative integer power: (2i)^(-1) = -0.5i
    z = DecimalComplex(0, 2)
    inv = z.power(DecimalComplex(-1, 0), ctx)
    assert inv.imag == Decimal("-0.5")

    # Real base with fractional power: (-4)^0.5 = 2i
    neg_real = DecimalComplex(-4, 0)
    frac_pow = neg_real.power(DecimalComplex("0.5", 0), ctx)
    assert frac_pow.real == Decimal(0)
    assert frac_pow.imag == Decimal(2)

    # Positive real base power
    pos_real = DecimalComplex(4, 0)
    assert pos_real.power(DecimalComplex("0.5", 0), ctx).real == Decimal(2)

