from Token import *
from tokentype import TokenType
from Expr import *
from error_handler import ErrorHandler
from Stmt import *

class Parser:
    class ParseError(RuntimeError):
        def __init__(self, message):
            super().__init__(message)

    def __init__(self, tokens, error_handler):
        self.error_handler = error_handler

        self.tokens = tokens 
        self._current = 0

    def expression(self): 
        return self.equality()

    def statement(self):
        if (self.match(TokenType.PRINT)): return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def equality(self):
        expr = self.comparison()

        while (self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr 

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr 

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr 

    def unary(self):
        if (self.match(TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if (self.match(TokenType.FALSE)):
            return Literal(False)
        if (self.match(TokenType.TRUE)):
            return Literal(True)
        if (self.match(TokenType.NIL)):
            return Literal(None)

        if (self.match(TokenType.NUMBER, TokenType.STRING)):
            return Literal(self.previous().literal)

        if (self.match(TokenType.LEFT_PAREN)):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

    def match(self, *types):
        for _type in types:
            if (self.check(_type)):
                self.advance()
                return True 

        return False

    def parse(self):
        statements = []
        while not self._isAtEnd():
            statements.append(self.statement())
        return statements

    def consume(self, _type, message):
        if (self.check(_type)): return self.advance()
        raise self.error(self.peek(), message)

    def check(self, _type):
        if self._isAtEnd(): return False 
        return self.peek().tokentype == _type 

    def advance(self):
        if not self._isAtEnd(): self._current += 1
        return self.previous()

    def _isAtEnd(self):
        return self.peek().tokentype == TokenType.EOF 

    def peek(self):
        return self.tokens[self._current]

    def previous(self):
        return self.tokens[self._current-1]

    def error(self, token, message):
        self.error_handler.error(token, message)
        return Parser.ParseError("")
