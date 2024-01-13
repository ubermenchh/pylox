import sys, os
from scanner import Scanner
from Token import *
from tokentype import TokenType
from Parser import *
from ast_printer import AstPrinter 
from runtime_error import RuntimeError_
from interpreter import Interpreter
from error_handler import ErrorHandler 

class Lox:
    def __init__(self):
        self.interpreter = Interpreter()
        self.error_handler = ErrorHandler()

    def run_file(self, path):
        with open(path, "r") as f:
            data = "".join(f.readlines())

        self.run(data)

        if self.error_handler.had_error:
            sys.exit(65)
        if self.error_handler.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                print("> ", end="")
                self.run(input())

                self.error_handler.had_error = False
                self.error_handler.had_runtime_error = False 
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")

    def run(self, source):
        scanner = Scanner(source, self.error_handler)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()

        if self.error_handler.had_error or self.error_handler.had_runtime_error: return

        self.interpreter.interpret(statements)

        #print(AstPrinter().print(statements)) 

if __name__=="__main__":
    lox = Lox()
    if len(sys.argv[1:]) > 1:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(sys.argv[1:]) == 1:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()
