from tokentype import TokenType


class Token:
    def __init__(self, tokentype, lexeme, literal, line):
        self.tokentype = tokentype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def to_string(self):
        return (
            f"<Token> {self.tokentype} | {self.lexeme} | {self.literal} | {self.line}"
        )

    def __str__(self):
        return self.to_string()
