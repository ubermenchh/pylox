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
        return self.assignment()

    def declaration(self):
        try:
            if self.match([TokenType.VAR]):
                return self.var_declaration()
            if self.match([TokenType.FUN]):
                return self.function("function")
            return self.statement()
        except Parser.ParseError as e:
            self.synchronize()
            return None

    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, "Expect " + kind + " name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after " + kind + " name.")
        parameters = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) > 255:
                    self.error(self.peek(), f"Don't wanna have more than 255 parameters to a {kind}")

                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected identifier."))

                if not self.match([TokenType.COMMA]):
                    break

            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

            self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
            body = self.block()
            return Function(name, parameters, body)

    def statement(self):
        if self.match([TokenType.PRINT]):
            return self.print_statement()
        if self.match([TokenType.IF]):
            return self.if_statement()
        if self.match([TokenType.WHILE]):
            return self.while_statement()
        if self.match([TokenType.FOR]):
            return self.for_statement()
        if self.match([TokenType.RETURN]):
            return self.return_statement()

        if self.match([TokenType.LEFT_BRACE]):
            return Block(self.block())

        return self.expression_statement()

    def return_statement(self):
        keyword = self.previous()
        value = None 
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if confition.")

        then_branch = self.statement()
        else_branch = None

        if self.match([TokenType.ELSE]):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def assignment(self):
        expr = self.or_()

        if self.match([TokenType.EQUAL]):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def or_(self):
        expr = self.and_()

        while self.match([TokenType.OR]):
            operator = self.previous()
            right = self.and_()
            expr = Logical(expr, operator, right)

        return expr

    def and_(self):
        expr = self.equality()

        while self.match([TokenType.AND]):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def block(self):
        statements = []

        while (not self.check(TokenType.RIGHT_BRACE) and not self._isAtEnd()):
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return While(condition, body)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = None
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        else:
            increment = None
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        if condition is not None:
            body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def equality(self):
        expr = self.comparison()

        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match([
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            ]):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()

        while self.match([TokenType.SLASH, TokenType.STAR]):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match([TokenType.LEFT_PAREN]):
                expr = self.finish_call(expr)
            else:
                break 

        return expr

    def finish_call(self, callee):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) > 255:
                    self.error(self.peek(), "Why do you need more than 255 arguments anyway?")

                arguments.append(self.assignment())

                if not self.match([TokenType.COMMA]):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)


    def primary(self):
        if self.match([TokenType.FALSE]):
            return Literal(False)
        if self.match([TokenType.TRUE]):
            return Literal(True)
        if self.match([TokenType.NIL]):
            return Literal(None)

        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.previous().literal)

        if self.match([TokenType.IDENTIFIER]):
            return Variable(self.previous())

        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

    def match(self, types):
        for _type in types:
            if self.check(_type):
                self.advance()
                return True

        return False

    def synchronize(self):
        self.advance()
        block_tokens = [
            TokenType.CLASS,
            TokenType.FUN,
            TokenType.VAR,
            TokenType.FOR,
            TokenType.IF,
            TokenType.WHILE,
            TokenType.PRINT,
            TokenType.RETURN,
        ]

        while not self._isAtEnd():
            if self.previous().tokentype == TokenType.SEMICOLON:
                return

            if self.peek().tokentype in block_tokens:
                return

            self.advance()

    def parse(self):
        statements = []
        while not self._isAtEnd():
            statements.append(self.declaration())
        return statements

    def consume(self, _type, message):
        if self.check(_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, _type):
        if self._isAtEnd():
            return False
        return self.peek().tokentype == _type

    def advance(self):
        if not self._isAtEnd():
            self._current += 1
        return self.previous()

    def _isAtEnd(self):
        return self.peek().tokentype == TokenType.EOF

    def peek(self):
        return self.tokens[self._current]

    def previous(self):
        return self.tokens[self._current - 1]

    def error(self, token, message):
        self.error_handler.error(token, message)
        return Parser.ParseError("")
