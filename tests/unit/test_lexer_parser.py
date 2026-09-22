"""Unit tests for the expression Lexer and Parser."""

import pytest
from decimal import Decimal
from src.engine.lexer import Lexer, TokenType
from src.engine.parser import (
    Parser,
    NumberNode,
    BinaryOpNode,
    UnaryOpNode,
    FunctionCallNode,
    ConstantNode
)
from src.engine.exceptions import SyntaxMathError, MismatchedParenthesesError

def test_lexer_tokens():
    lexer = Lexer("(15.5 + 2.75) * sqrt(144) ^ 2")
    tokens = lexer.tokenize()
    types = [t.type for t in tokens]
    assert types == [
        TokenType.LPAREN, TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER, TokenType.RPAREN,
        TokenType.MULTIPLY, TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.NUMBER, TokenType.RPAREN,
        TokenType.POWER, TokenType.NUMBER, TokenType.EOF
    ]

def test_lexer_unexpected_character():
    lexer = Lexer("10 + $")
    with pytest.raises(SyntaxMathError) as exc:
        lexer.tokenize()
    assert exc.value.position == 5

def test_lexer_multiple_dots():
    lexer = Lexer("10.5.2 + 1")
    with pytest.raises(SyntaxMathError):
        lexer.tokenize()

def test_parser_basic_expression():
    tokens = Lexer("2 + 3 * 4").tokenize()
    ast = Parser(tokens).parse()
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == '+'
    assert isinstance(ast.left, NumberNode) and ast.left.value == Decimal(2)
    assert isinstance(ast.right, BinaryOpNode) and ast.right.op == '*'

def test_parser_unary_minus():
    tokens = Lexer("-5 + 3").tokenize()
    ast = Parser(tokens).parse()
    assert isinstance(ast, BinaryOpNode)
    assert isinstance(ast.left, UnaryOpNode)
    assert ast.left.op == '-'

def test_parser_function_call():
    tokens = Lexer("sqrt(100)").tokenize()
    ast = Parser(tokens).parse()
    assert isinstance(ast, FunctionCallNode)
    assert ast.name == "sqrt"
    assert len(ast.args) == 1

def test_parser_mismatched_parentheses():
    with pytest.raises(MismatchedParenthesesError):
        Parser(Lexer("(2 + 3").tokenize()).parse()

    with pytest.raises(MismatchedParenthesesError):
        Parser(Lexer("2 + 3)").tokenize()).parse()

def test_parser_empty_expression():
    with pytest.raises(SyntaxMathError):
        Parser(Lexer("").tokenize()).parse()
