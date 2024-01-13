from tokentype import TokenType
from Token import Token
from error_handler import ErrorHandler

class Scanner:
    def __init__(self, source, error_handler):
        self.error_handler = error_handler

        self.source = source 
        self.tokens = []

        self._start = 0
        self._current = 0
        self._line = 1

        self.keywords = {
                "add": TokenType.AND,
                "class": TokenType.CLASS,
                "else": TokenType.ELSE,
                "false": TokenType.FALSE,
                "for": TokenType.FOR,
                "fun": TokenType.FUN,
                "if": TokenType.IF,
                "nil": TokenType.NIL,
                "or": TokenType.OR,
                "print": TokenType.PRINT,
                "return": TokenType.RETURN,
                "super": TokenType.SUPER,
                "true": TokenType.TRUE,
                "var": TokenType.VAR,
                "while": TokenType.WHILE
                }

    def _isAtEnd(self):
        return self._current >= len(self.source)

    def scan_tokens(self):
        while not self._isAtEnd():
            self._start = self._current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self.tokens 

    def scan_token(self):
        c = self.advance()

        if   c == "(": self.add_token(TokenType.LEFT_PAREN)
        elif c == ")": self.add_token(TokenType.RIGHT_PAREN) 
        elif c == "{": self.add_token(TokenType.LEFT_BRACE) 
        elif c == "}": self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",": self.add_token(TokenType.COMMA) 
        elif c ==  ".": self.add_token(TokenType.DOT) 
        elif c == "-": self.add_token(TokenType.MINUS) 
        elif c == "+": self.add_token(TokenType.PLUS) 
        elif c == ";": self.add_token(TokenType.SEMICOLON)
        elif c == "*": self.add_token(TokenType.STAR)

        elif c == "!":
            if self._match("="):
                self.add_token(TokenType.BANG_EQUAL)
            else:
                self.add_token(TokenType.BANG)
            return

        elif c == "=":
            if self._match("="):
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.EQUAL)
            return

        elif c == "<":
            if self._match("="):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
            return 

        elif c == ">":
            if self._match("="):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
            return 
            
        elif c == "/":
            if self._match("/"):
                while(self.peek() != '\n' and not self._isAtEnd()): self.advance()
            else:
                self.add_token(TokenType.SLASH)
            return 
            
        elif c == " ": pass 
        elif c == "\r": pass
        elif c == "\t": return 
        elif c == "\n":
            self._line += 1
            return 

        elif c == '"': self._string(); return 

        else:
            if c.isdigit():
                self.number()
            elif c.isalpha():
                self.identifier()
            else:
                self.error_handler.error(self._line, "Unexpected character.")
            return

    def identifier(self):
        while self.peek().isalnum(): self.advance()

        text = self.source[self._start:self._current]
        _type = self.keywords[text]
        if _type is None: _type = TokenType.INDENTIFIER
        self.add_token(_type)

    def _string(self):
        while self.peek() != '"' and not self._isAtEnd():
            if (self.peek() == '\n'): self._line += 1
            self.advance()

        if (self._isAtEnd()):
            self.error_handler.error(self._line, "Unterminated string.")
            return 
        
        # Closing "
        self.advance()

        value = self.source[self._start+1:self._current-1]
        self.add_token(TokenType.STRING, value)

    def advance(self):
        self._current += 1
        return self.source[self._current - 1]

    def add_token(self, tokentype, literal=None):
        text = self.source[self._start:self._current]
        self.tokens.append(Token(tokentype, text, literal, self._line))

    def _match(self, expected):
        if self._isAtEnd(): return False 
        if self.source[self._current] != expected: return False 

        self._current += 1
        return True

    def peek(self):
        if self._isAtEnd(): return '\0'
        return self.source[self._current]

    def peek_next(self):
        if (self._current + 1 >= len(self.source)): return '\0'
        return self.source[self._current+1]
 
    def number(self):
        while self.peek().isdigit(): self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            # Consume the "."
            self.advance()

            while self.isDigit(self.peek()): self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self._start:self._current]))
