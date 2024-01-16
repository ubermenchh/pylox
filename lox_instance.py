from lox_class import *

class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def to_string(self):
        return f"{self.klass.name} instance."

    def get(self, name):
        if name.lexeme in self.fields.keys():
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError_(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value
