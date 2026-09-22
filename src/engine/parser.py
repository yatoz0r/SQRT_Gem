"""Recursive Descent Parser for mathematical expressions producing an Abstract Syntax Tree (AST)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from src.engine.lexer import Token, TokenType
from src.engine.exceptions import SyntaxMathError, MismatchedParenthesesError

class ASTNode(ABC):
    position: int

@dataclass
class NumberNode(ASTNode):
    value: Decimal
    position: int

@dataclass
class ConstantNode(ASTNode):
    name: str
    position: int

@dataclass
class UnaryOpNode(ASTNode):
    op: str
    operand: ASTNode
    position: int

@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode
    position: int

@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]
    position: int

class Parser:
    """Parses a sequence of tokens into an AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.cursor = 0

    def _peek(self) -> Token:
        if self.cursor < len(self.tokens):
            return self.tokens[self.cursor]
        return self.tokens[-1]

    def _previous(self) -> Token:
        return self.tokens[self.cursor - 1]

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.cursor += 1
        return self._previous()

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def parse(self) -> ASTNode:
        if self._is_at_end():
            raise SyntaxMathError("Empty expression", position=0)
        node = self._expression()
        if not self._is_at_end():
            token = self._peek()
            if token.type == TokenType.RPAREN:
                raise MismatchedParenthesesError(position=token.position)
            raise SyntaxMathError(f"Unexpected token '{token.value}' after expression", position=token.position)
        return node

    def _expression(self) -> ASTNode:
        return self._term()

    def _term(self) -> ASTNode:
        node = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_token = self._previous()
            right = self._factor()
            node = BinaryOpNode(op=op_token.value, left=node, right=right, position=op_token.position)
        return node

    def _factor(self) -> ASTNode:
        node = self._power()
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self._previous()
            right = self._power()
            node = BinaryOpNode(op=op_token.value, left=node, right=right, position=op_token.position)
        return node

    def _power(self) -> ASTNode:
        node = self._unary()
        if self._match(TokenType.POWER):
            op_token = self._previous()
            # Right-associative exponentiation: 2^3^2 = 2^(3^2)
            right = self._power()
            node = BinaryOpNode(op=op_token.value, left=node, right=right, position=op_token.position)
        return node

    def _unary(self) -> ASTNode:
        if self._match(TokenType.PLUS, TokenType.MINUS):
            op_token = self._previous()
            operand = self._unary()
            return UnaryOpNode(op=op_token.value, operand=operand, position=op_token.position)
        return self._primary()

    def _primary(self) -> ASTNode:
        token = self._peek()

        if self._match(TokenType.NUMBER):
            num_token = self._previous()
            try:
                val = Decimal(num_token.value)
            except Exception as e:
                raise SyntaxMathError(f"Invalid decimal literal: {str(e)}", position=num_token.position)
            return NumberNode(value=val, position=num_token.position)

        if self._match(TokenType.IDENTIFIER):
            ident_token = self._previous()
            ident_name = ident_token.value.lower()

            if self._match(TokenType.LPAREN):
                lparen = self._previous()
                args: List[ASTNode] = []
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._expression())
                        if not self._match(TokenType.COMMA):
                            break
                if not self._match(TokenType.RPAREN):
                    raise MismatchedParenthesesError(position=lparen.position)
                return FunctionCallNode(name=ident_name, args=args, position=ident_token.position)
            else:
                return ConstantNode(name=ident_name, position=ident_token.position)

        if self._match(TokenType.LPAREN):
            lparen = self._previous()
            expr_node = self._expression()
            if not self._match(TokenType.RPAREN):
                raise MismatchedParenthesesError(position=lparen.position)
            return expr_node

        if self._is_at_end():
            raise SyntaxMathError("Unexpected end of expression", position=token.position)

        raise SyntaxMathError(f"Unexpected token '{token.value}'", position=token.position)
