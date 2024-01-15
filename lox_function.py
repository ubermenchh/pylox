from lox_callable import *
from Environment import *
from interpreter import *
from Return import *

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(interpreter.globals)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value
        
        return None

    def __str__(self):
        return f"<Function '{self.declaration.name.lexeme}'>"
