from tokentype import TokenType
from token import Token
from lox import Lox

class Scanner:
    def __init__(self, source):
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
        return self._current > len(self.source)

    def scan_tokens(self):
        while not self._iAtEnd():
            self._start = self._current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self.tokens 

    def scan_token(self):
        c = self.advance()
        match c:
            case "(": self.add_token(TokenType.LEFT_PAREN); return
            case ")": self.add_token(TokenType.RIGHT_PAREN); return 
            case "{": self.add_token(TokenType.LEFT_BRACE); return 
            case "}": self.add_token(TokenType.RIGHT_BRACE); return
            case ",": self.add_token(TokenType.COMMA); return 
            case ".": self.add_token(TokenType.DOT); return 
            case "-": self.add_token(TokenType.MINUS); return 
            case "+": self.add_token(TokenType.PLUS); return 
            case ";": self.add_token(TokenType.SEMICOLON); return 
            case "*": self.add_token(TokenType.STAR); return

            case "!":
                if self._match("="):
                    self.add_token(TokenType.BANG_EQUAL)
                else:
                    self.add_token(TokenType.BANG)
                return

            case "=":
                if self._match("="):
                    self.add_token(TokenType.EQUAL_EQUAL)
                else:
                    self.add_token(TokenType.EQUAL)
                return

            case "<":
                if self._match("="):
                    self.add_token(TokenType.LESS_EQUAL)
                else:
                    self.add_token(TokenType.LESS)
                return 

            case ">":
                if self._match("="):
                    self.add_token(TokenType.GREATER_EQUAL)
                else:
                    self.add_token(TokenType.GREATER)
                return 
            
            case "/":
                if self._match("/"):
                    while(self.peek() != '\n' and not self._isAtEnd()): self.advance()
                else:
                    self.add_token(TokenType.SLASH)
                return 
            
            case " ": pass 
            case "\r": pass
            case "\t": return 
            case "\n":
                self._line += 1
                return 

            case '"': self._string(); return 

            case _  :
                if self.isDigit(c):
                    self.number()
                elif self.isAlpha(c):
                    self.identifier()
                else:
                    Lox.error(self._line, "Unexpected character.")
                return

    def identifier(self):
        while self.isAlphaNumeric(self.peek()): self.advance()

        text = self.source[self._start:self._current]
        _type = keywords[text]
        if (_type == None): _type = INDENTIFIER
        self.add_token(TokenType._type)

    def _string(self):
        while self.peek() != '"' and not self._isAtEnd():
            if (self.peek() == '\n'): self._line += 1
            self.advance()

        if (self._isAtEnd()):
            Lox.error(self._line, "Unterminated string.")
            return 
        
        # Closing "
        self.advance()

        value = self.source[self._start+1:self._current+1]
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

    def isAlpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'
    
    def isAlphaNumeric(self, c):
        return self.isAlpha(c) or self.isDigit(c) 
    
    def isDigit(self, c):
        return c >= '0' and c <= '9'

    def number(self):
        while self.isDigit(self.peek()): self.advance()

        if self.peek() == '.' and self.isDigit(self.peek_next()):
            # Consume the "."
            self.advance()

            while self.isDigit(self.peek()): self.advance()

        self.add_token(TokenType.NUMBER, int(self.source[self._start:self._current]))
