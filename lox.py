import sys, os
from scanner import Scanner
from token import *
from tokentype import TokenType
from parser import *
from ast_printer import *

class Lox:
    def __init__(self):
        self.had_error = False 

    def run_file(self, path):
        if self.had_error:
            sys.exit(65)
        
        with open(path, "r") as f:
            data = f.read()
        self.run(data)

    def run_prompt(self):
        while True:
            try:
                line = input("> ")
                if line is None:
                    break 
                self.run(line)
                self.had_error = False 
            except EOFError: break 

    def run(self, source):
        tokens = Scanner.scan_tokens(source)
        parser = Parser(tokens)
        expression = parser.parse()

        if self.had_error: return 

        print(AstPrinter().print(expression))
    
    # Error Handling
    def error(self, token, message):
        if token.tokentype == TokenType.EOF:
            self.report(token.line, "", message)
        else:
            self.report(token.line, " at '" + token.lexeme + "'", message)

    def report(self, line, where, message):
        print(f"Line {line} - Error {where}: {message}", file=sys.stderr)
        self.had_error = True 

if __name__=="__main__":
    if len(sys.argv) > 1:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv) == 1:
        Lox.run_file(sys.argv[0])
    else:
        Lox.run_prompt()
