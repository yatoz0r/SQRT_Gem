"""High-precision arbitrary-length complex numbers on top of decimal module.

Satisfies Section 1 of TZ_dopolnenie.md:
'1. Функциональность: комплексные длинные числа, заданная точность, аналитические выражения, текстовый ввод'
"""

from decimal import Decimal, Context, ROUND_HALF_UP
from typing import Union
from src.engine.exceptions import (
    DivisionByZeroError,
    MathEngineError
)

class DecimalComplex:
    """Arbitrary-precision complex number z = a + bi with Decimal components."""

    def __init__(self, real: Union[Decimal, int, float, str] = 0, imag: Union[Decimal, int, float, str] = 0):
        self.real = Decimal(str(real)) if not isinstance(real, Decimal) else real
        self.imag = Decimal(str(imag)) if not isinstance(imag, Decimal) else imag

    @property
    def is_real(self) -> bool:
        """Returns True if the imaginary part is zero."""
        return self.imag == 0

    def add(self, other: "DecimalComplex", context: Context) -> "DecimalComplex":
        return DecimalComplex(
            context.add(self.real, other.real),
            context.add(self.imag, other.imag)
        )

    def subtract(self, other: "DecimalComplex", context: Context) -> "DecimalComplex":
        return DecimalComplex(
            context.subtract(self.real, other.real),
            context.subtract(self.imag, other.imag)
        )

    def multiply(self, other: "DecimalComplex", context: Context) -> "DecimalComplex":
        # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        ac = context.multiply(self.real, other.real)
        bd = context.multiply(self.imag, other.imag)
        ad = context.multiply(self.real, other.imag)
        bc = context.multiply(self.imag, other.real)
        return DecimalComplex(
            context.subtract(ac, bd),
            context.add(ad, bc)
        )

    def divide(self, other: "DecimalComplex", context: Context, position: int = -1) -> "DecimalComplex":
        # (a + bi) / (c + di) = [(ac + bd) + (bc - ad)i] / (c^2 + d^2)
        c2 = context.multiply(other.real, other.real)
        d2 = context.multiply(other.imag, other.imag)
        denom = context.add(c2, d2)
        if denom == 0:
            raise DivisionByZeroError(position=position)

        ac = context.multiply(self.real, other.real)
        bd = context.multiply(self.imag, other.imag)
        bc = context.multiply(self.imag, other.real)
        ad = context.multiply(self.real, other.imag)

        num_real = context.add(ac, bd)
        num_imag = context.subtract(bc, ad)

        return DecimalComplex(
            context.divide(num_real, denom),
            context.divide(num_imag, denom)
        )

    def power(self, exponent: "DecimalComplex", context: Context, position: int = -1) -> "DecimalComplex":
        """Computes z ** exponent. Supports arbitrary integer exponents and real powers."""
        if self.real == 0 and self.imag == 0:
            if exponent.real <= 0:
                raise DivisionByZeroError(position=position)
            return DecimalComplex(0, 0)

        # Integer exponentiation via binary exponentiation
        if exponent.imag == 0 and exponent.real == exponent.real.to_integral_value():
            n = int(exponent.real)
            if n == 0:
                return DecimalComplex(1, 0)
            if n < 0:
                pos_power = self.power(DecimalComplex(-n, 0), context, position)
                return DecimalComplex(1, 0).divide(pos_power, context, position)

            res = DecimalComplex(1, 0)
            base = DecimalComplex(self.real, self.imag)
            while n > 0:
                if n % 2 == 1:
                    res = res.multiply(base, context)
                base = base.multiply(base, context)
                n //= 2
            return res

        # Real base with real fractional power
        if self.imag == 0 and exponent.imag == 0:
            if self.real < 0:
                # (-x)^(p/q)
                abs_val = context.power(-self.real, exponent.real)
                # If exponent is 0.5 (sqrt), returns i * sqrt(x)
                if exponent.real == Decimal("0.5"):
                    return DecimalComplex(0, abs_val)
            else:
                return DecimalComplex(context.power(self.real, exponent.real), 0)

        raise MathEngineError("Arbitrary complex fractional power is currently unsupported", code="COMPLEX_POWER_ERROR", position=position)

    def abs(self, context: Context) -> Decimal:
        """Returns the Euclidean magnitude |z| = sqrt(a^2 + b^2)."""
        if self.imag == 0:
            return abs(self.real)
        if self.real == 0:
            return abs(self.imag)
        a2 = context.multiply(self.real, self.real)
        b2 = context.multiply(self.imag, self.imag)
        return context.sqrt(context.add(a2, b2))

    def sqrt(self, context: Context) -> "DecimalComplex":
        """Principal square root of a complex number with arbitrary precision."""
        if self.imag == 0:
            if self.real >= 0:
                return DecimalComplex(context.sqrt(self.real), 0)
            else:
                return DecimalComplex(0, context.sqrt(-self.real))

        # Formula: sqrt(a + bi) = sqrt((|z| + a) / 2) + i * sgn(b) * sqrt((|z| - a) / 2)
        mod_z = self.abs(context)
        two = Decimal(2)
        re_part = context.sqrt(context.divide(context.add(mod_z, self.real), two))
        im_mag = context.sqrt(context.divide(context.subtract(mod_z, self.real), two))
        im_part = im_mag if self.imag >= 0 else -im_mag

        return DecimalComplex(re_part, im_part)

    def format(self, precision: int) -> str:
        """Formats the complex number into human-readable string with requested precision."""
        from src.engine.decimal_math import format_result

        # Check if imaginary part is effectively 0 under the given precision
        re_str = format_result(self.real, precision)
        im_str = format_result(self.imag, precision)


        im_is_zero = self.imag == 0 or Decimal(im_str) == 0
        re_is_zero = self.real == 0 or Decimal(re_str) == 0

        if im_is_zero:
            return re_str

        # Pure imaginary
        if re_is_zero:
            if self.imag == 1 or im_str == "1":
                return "i"
            elif self.imag == -1 or im_str == "-1":
                return "-i"
            return f"{im_str}i"

        # General a + bi
        if self.imag > 0:
            im_display = "" if (self.imag == 1 or im_str == "1") else im_str
            return f"{re_str} + {im_display}i" if im_display else f"{re_str} + i"
        else:
            abs_im = format_result(-self.imag, precision)
            im_display = "" if (-self.imag == 1 or abs_im == "1") else abs_im
            return f"{re_str} - {im_display}i" if im_display else f"{re_str} - i"


    def __repr__(self) -> str:
        if self.imag == 0:
            return f"DecimalComplex({self.real})"
        return f"DecimalComplex({self.real} + {self.imag}i)"
