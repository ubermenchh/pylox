import sys

from Token import Token
from tokentype import TokenType
from runtime_error import RuntimeError_


class ErrorHandler:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False

    def error(self, token, message):
        if token.tokentype == TokenType.EOF:
            self.report(token.line, "", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", message)

    def runtime_error(self, error):
        print(f"[Line {error.token.line}] --> {error.message}")
        self.had_error = True
        self.had_runtime_error = True

    def report(self, line, where, message):
        print(f"Line {line} | Error {where}: {message}", file=sys.stderr)
        self.had_error = True
