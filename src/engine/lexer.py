"""Lexer (Tokenizer) for mathematical expressions."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List
from src.engine.exceptions import SyntaxMathError

class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    IDENTIFIER = auto()
    EOF = auto()

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int

class Lexer:
    """Tokenizes mathematical expression strings into a stream of Tokens."""
    
    def __init__(self, expression: str):
        self.text = expression
        self.pos = 0
        self.length = len(expression)
        
    def _peek(self) -> str:
        if self.pos < self.length:
            return self.text[self.pos]
        return '\0'
        
    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        
        while self.pos < self.length:
            ch = self._peek()
            
            if ch.isspace():
                self._advance()
                continue
                
            start_pos = self.pos
            
            if ch.isdigit() or ch == '.':
                num_str = self._consume_number()
                tokens.append(Token(TokenType.NUMBER, num_str, start_pos))
            elif ch.isalpha() or ch == '_':
                ident = self._consume_identifier()
                tokens.append(Token(TokenType.IDENTIFIER, ident, start_pos))
            elif ch == '+':
                self._advance()
                tokens.append(Token(TokenType.PLUS, '+', start_pos))
            elif ch == '-':
                self._advance()
                tokens.append(Token(TokenType.MINUS, '-', start_pos))
            elif ch == '*':
                self._advance()
                tokens.append(Token(TokenType.MULTIPLY, '*', start_pos))
            elif ch == '/':
                self._advance()
                tokens.append(Token(TokenType.DIVIDE, '/', start_pos))
            elif ch == '^':
                self._advance()
                tokens.append(Token(TokenType.POWER, '^', start_pos))
            elif ch == '(':
                self._advance()
                tokens.append(Token(TokenType.LPAREN, '(', start_pos))
            elif ch == ')':
                self._advance()
                tokens.append(Token(TokenType.RPAREN, ')', start_pos))
            elif ch == ',':
                self._advance()
                tokens.append(Token(TokenType.COMMA, ',', start_pos))
            else:
                raise SyntaxMathError(f"Unexpected character '{ch}'", position=start_pos)
                
        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens

    def _consume_number(self) -> str:
        start = self.pos
        has_dot = False
        
        while self.pos < self.length:
            ch = self._peek()
            if ch == '.':
                if has_dot:
                    raise SyntaxMathError("Multiple decimal points in number", position=self.pos)
                has_dot = True
                self._advance()
            elif ch.isdigit():
                self._advance()
            else:
                break
                
        val = self.text[start:self.pos]
        if val == '.':
            raise SyntaxMathError("Single '.' is not a valid number", position=start)
        return val

    def _consume_identifier(self) -> str:
        start = self.pos
        while self.pos < self.length and (self._peek().isalnum() or self._peek() == '_'):
            self._advance()
        return self.text[start:self.pos]
