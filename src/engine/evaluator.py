"""Evaluator for AST nodes in the mathematical engine supporting arbitrary precision real and complex numbers."""

import time
from dataclasses import dataclass
from decimal import Decimal, Context
from typing import Dict, Any, Union
from src.engine.lexer import Lexer
from src.engine.parser import (
    Parser,
    ASTNode,
    NumberNode,
    ConstantNode,
    UnaryOpNode,
    BinaryOpNode,
    FunctionCallNode
)
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
from src.engine.complex_math import DecimalComplex
from src.engine.exceptions import (
    UnknownIdentifierError,
    SyntaxMathError,
    NegativeSqrtError,
    MathEngineError
)

@dataclass(frozen=True)
class CalculationResult:
    expression: str
    raw_value: Union[Decimal, DecimalComplex]
    formatted_value: str
    precision: int
    elapsed_ms: float
    digits_count: int
    is_complex: bool = False

class MathEngine:
    """Core mathematical calculation engine providing arbitrary precision analytical evaluation."""

    def __init__(self):
        pass

    def evaluate(self, expression: str, precision: int = 50, allow_complex: bool = False) -> CalculationResult:
        """
        Parses and computes the mathematical expression with the given precision.
        Returns a CalculationResult containing the formatted and raw values.
        Supports both real Decimal and arbitrary-length DecimalComplex numbers.
        """
        if not expression or not expression.strip():
            raise SyntaxMathError("Expression cannot be empty", position=0)

        start_time = time.perf_counter()
        context = get_calculation_context(precision)

        lexer = Lexer(expression)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        # If user explicitly wrote 'i' or passed allow_complex=True, enable complex support
        has_imaginary_unit = any(t.value.lower() == 'i' for t in tokens if hasattr(t, 'value'))
        effective_complex = allow_complex or has_imaginary_unit

        complex_res = self._eval_node(ast, context, precision, effective_complex)

        if complex_res.is_real:
            raw_value = complex_res.real
            formatted_str = format_result(complex_res.real, precision)
            is_complex = False
        else:
            raw_value = complex_res
            formatted_str = complex_res.format(precision)
            is_complex = True

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        digits_count = len(formatted_str.replace("-", "").replace(".", "").replace("+", "").replace("i", "").replace(" ", ""))

        return CalculationResult(
            expression=expression.strip(),
            raw_value=raw_value,
            formatted_value=formatted_str,
            precision=precision,
            elapsed_ms=elapsed_ms,
            digits_count=digits_count,
            is_complex=is_complex
        )

    def _eval_node(self, node: ASTNode, context: Context, precision: int, allow_complex: bool) -> DecimalComplex:
        if isinstance(node, NumberNode):
            return DecimalComplex(node.value, 0)

        if isinstance(node, ConstantNode):
            return self._eval_constant(node, precision)

        if isinstance(node, UnaryOpNode):
            val = self._eval_node(node.operand, context, precision, allow_complex)
            if node.op == '+':
                return val
            elif node.op == '-':
                return DecimalComplex(-val.real, -val.imag)
            raise SyntaxMathError(f"Unsupported unary operator '{node.op}'", position=node.position)

        if isinstance(node, BinaryOpNode):
            left = self._eval_node(node.left, context, precision, allow_complex)
            right = self._eval_node(node.right, context, precision, allow_complex)
            return self._eval_binary(node.op, left, right, context, node.position)

        if isinstance(node, FunctionCallNode):
            return self._eval_function(node, context, precision, allow_complex)

        raise MathEngineError(f"Unknown AST node: {type(node).__name__}")

    def _eval_constant(self, node: ConstantNode, precision: int) -> DecimalComplex:
        name = node.name.lower()
        if name == "pi":
            return DecimalComplex(compute_pi(precision), 0)
        elif name == "e":
            return DecimalComplex(compute_e(precision), 0)
        elif name == "i":
            return DecimalComplex(0, 1)
        raise UnknownIdentifierError(node.name, position=node.position)

    def _eval_binary(self, op: str, left: DecimalComplex, right: DecimalComplex, context: Context, position: int) -> DecimalComplex:
        if op == '+':
            return left.add(right, context)
        elif op == '-':
            return left.subtract(right, context)
        elif op == '*':
            return left.multiply(right, context)
        elif op == '/':
            return left.divide(right, context, position=position)
        elif op == '^':
            return left.power(right, context, position=position)
        raise SyntaxMathError(f"Unsupported binary operator '{op}'", position=position)

    def _eval_function(self, node: FunctionCallNode, context: Context, precision: int, allow_complex: bool) -> DecimalComplex:
        name = node.name.lower()
        args = node.args

        if name == "sqrt":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'sqrt' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision, allow_complex)
            if arg_val.is_real and arg_val.real < 0 and not allow_complex:
                raise NegativeSqrtError(position=node.position)
            return arg_val.sqrt(context)

        elif name == "abs":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'abs' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision, allow_complex)
            return DecimalComplex(arg_val.abs(context), 0)

        elif name == "ln":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'ln' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision, allow_complex)
            if arg_val.is_real:
                return DecimalComplex(compute_ln(arg_val.real, context, position=node.position), 0)
            raise MathEngineError("Complex logarithm is not currently enabled", code="COMPLEX_LN_UNSUPPORTED", position=node.position)

        elif name == "exp":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'exp' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision, allow_complex)
            if arg_val.is_real:
                return DecimalComplex(compute_exp(arg_val.real, context, position=node.position), 0)
            raise MathEngineError("Complex exponential is not currently enabled", code="COMPLEX_EXP_UNSUPPORTED", position=node.position)

        raise UnknownIdentifierError(node.name, position=node.position)
