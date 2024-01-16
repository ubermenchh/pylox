from lox_callable import *
from Environment import *
from interpreter import *
from Return import *
from Environment import *
from lox_function import *

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, is_initializer):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return_ as return_value:
            if self.is_initializer: return self.closure.get_at(0, "self")

            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "self")
        return None

    def __str__(self):
        return f"<Function '{self.declaration.name.lexeme}'>"

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("self", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)
