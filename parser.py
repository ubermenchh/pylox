from token import *
from tokentype import TokenType
from Expr import *
from lox import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self._current = 0

    def expression(self): 
        return self.equality()

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
            expr = Expr.Binary(expr, operator, right)
        
        return expr 

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)
        return expr 

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)

        return expr 

    def unary(self):
        if (self.match(TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)

        return self.primary()

    def primary(self):
        if (self.match(TokenType.FALSE)):
            return Expr.Literal(False)
        if (self.match(TokenType.TRUE)):
            return Expr.Literal(True)
        if (self.match(TokenType.NIL)):
            return Expr.Literal(None)

        if (self.match(TokenType.NUMBER, TokenType.STRING)):
            return Expr.Literal(self.previous().literal)

        if (self.match(TokenType.LEFT_PAREN)):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)

    def match(self, *types):
        for _type in types:
            if (check(_type)):
                self.advance()
                return True 

        return False 

    def consume(self, _type, message):
        if (self.check(_type)): return self.advance()
        raise self.error(self.peek(), message)

    def check(self, _type):
        if self.isAtEnd(): return False 
        return self.peek().tokentype == _type 

    def advance(self):
        if not self.isAtEnd(): self._current += 1
        return self.previous()

    def isAtEnd(self):
        return self.peek().tokentype == TokenType.EOF 

    def peek(self):
        return self.tokens[self._current]

    def previous(self):
        return self.tokens[self._current-1]

    def error(self, token, message):
        Lox.error(token, message)
        return Parser.ParseError("")
