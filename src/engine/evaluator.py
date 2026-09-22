"""Evaluator for AST nodes in the mathematical engine."""

import time
from dataclasses import dataclass
from decimal import Decimal, Context
from typing import Dict, Any
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
from src.engine.exceptions import (
    UnknownIdentifierError,
    SyntaxMathError,
    MathEngineError
)

@dataclass(frozen=True)
class CalculationResult:
    expression: str
    raw_value: Decimal
    formatted_value: str
    precision: int
    elapsed_ms: float
    digits_count: int

class MathEngine:
    """Core mathematical calculation engine providing arbitrary precision analytical evaluation."""

    def __init__(self):
        pass

    def evaluate(self, expression: str, precision: int = 50) -> CalculationResult:
        """
        Parses and computes the mathematical expression with the given precision.
        Returns a CalculationResult containing the formatted and raw values.
        """
        if not expression or not expression.strip():
            raise SyntaxMathError("Expression cannot be empty", position=0)

        start_time = time.perf_counter()
        context = get_calculation_context(precision)

        lexer = Lexer(expression)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        raw_value = self._eval_node(ast, context, precision)
        formatted_str = format_result(raw_value, precision)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 3)
        digits_count = len(formatted_str.replace("-", "").replace(".", ""))

        return CalculationResult(
            expression=expression.strip(),
            raw_value=raw_value,
            formatted_value=formatted_str,
            precision=precision,
            elapsed_ms=elapsed_ms,
            digits_count=digits_count
        )

    def _eval_node(self, node: ASTNode, context: Context, precision: int) -> Decimal:
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, ConstantNode):
            return self._eval_constant(node, precision)

        if isinstance(node, UnaryOpNode):
            val = self._eval_node(node.operand, context, precision)
            if node.op == '+':
                return val
            elif node.op == '-':
                return -val
            raise SyntaxMathError(f"Unsupported unary operator '{node.op}'", position=node.position)

        if isinstance(node, BinaryOpNode):
            left = self._eval_node(node.left, context, precision)
            right = self._eval_node(node.right, context, precision)
            return self._eval_binary(node.op, left, right, context, node.position)

        if isinstance(node, FunctionCallNode):
            return self._eval_function(node, context, precision)

        raise MathEngineError(f"Unknown AST node: {type(node).__name__}")

    def _eval_constant(self, node: ConstantNode, precision: int) -> Decimal:
        name = node.name.lower()
        if name == "pi":
            return compute_pi(precision)
        elif name == "e":
            return compute_e(precision)
        raise UnknownIdentifierError(node.name, position=node.position)

    def _eval_binary(self, op: str, left: Decimal, right: Decimal, context: Context, position: int) -> Decimal:
        if op == '+':
            return context.add(left, right)
        elif op == '-':
            return context.subtract(left, right)
        elif op == '*':
            return context.multiply(left, right)
        elif op == '/':
            return compute_divide(left, right, context, position=position)
        elif op == '^':
            return compute_power(left, right, context, position=position)
        raise SyntaxMathError(f"Unsupported binary operator '{op}'", position=position)

    def _eval_function(self, node: FunctionCallNode, context: Context, precision: int) -> Decimal:
        name = node.name.lower()
        args = node.args

        if name == "sqrt":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'sqrt' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision)
            return compute_sqrt(arg_val, context, position=node.position)

        elif name == "abs":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'abs' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision)
            return abs(arg_val)

        elif name == "ln":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'ln' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision)
            return compute_ln(arg_val, context, position=node.position)

        elif name == "exp":
            if len(args) != 1:
                raise SyntaxMathError(f"Function 'exp' takes exactly 1 argument ({len(args)} provided)", position=node.position)
            arg_val = self._eval_node(args[0], context, precision)
            return compute_exp(arg_val, context, position=node.position)

        raise UnknownIdentifierError(node.name, position=node.position)
