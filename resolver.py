from visitor import *
from Expr import *
from Stmt import *
from lox import Lox

import enum
from typing import List

class FunctionType(enum.Enum):
    NONE = enum.auto()
    FUNCTION = enum.auto()
    INITIALIZER = enum.auto()
    METHOD = enum.auto()

class ClassType(enum.Enum):
    NONE = enum.auto()
    CLASS = enum.auto()
    SUBCLASS = enum.auto()

class Resolver(Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.reolve(stmt.statements)
        self.end_scope()
        return None

    def visit_class_stmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if (stmt.superclass is not None) and (stmt.name.lexeme == stmt.superclass.name.lexeme):
            Lox.error(stmt.superclass.name, "A class can't inherit from itself.")

        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            self.resolve(stmt.superclass)

        if stmt.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["self"] = True
        
        for method in stmt.methods:
            declaration = FunctionType.METHOD

            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method, declaration)

        self.end_scope()

        if stmt.superclass is not None: self.end_scope()

        self.current_class = enclosing_class

        return None

    def resolve(self, statements):

        if isinstance(statements, List):
            for statement in statements:
                self.resolve_(statement)
            return 
        statements.accept(self)

    def resolve_(self, expr):
        expr.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)

        self.define(stmt.name) 

    def declare(self, name):
        if not self.scopes:
            return 

        scope = self.scopes[-1]
        
        if name.lexeme in scope.keys():
            Lox.error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False 

    def define(self, name):
        if not self.scopes:
            return 
        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def visit_variable_expr(self, expr):
        if (self.scopes and self.scopes[-1].get(expr.name.lexeme) is False):
            Lox.error(expr.name, "Can't read local variable is its own initializer.")

        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr, name):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return 

    def visit_assign_expr(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)
        return None 

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def resolve_function(self, function, type_):
        enclosing_function = self.current_function
        self.current_function = type_ 

        self.begin_scope()

        for param in function.params:
            self.declare(param)
            self.define(param)

        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_expression_stmt(self, stmt):
        self.resolve_(stmt.expression)
        return None

    def visit_if_stmt(self, stmt):
        self.resolve_(stmt.condition)
        self.resolve_(stmt.then_branch)

        if stmt.else_branch is not None:
            self.resolve_(stmt.else_branch)

        return None 

    def visit_print_stmt(self, stmt):
        self.resolve_(stmt.expression)
        return None 

    def visit_return_stmt(self, stmt):
        if self.current_function == FunctionType.NONE:
            Lox.error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                Lox.error(stmt.keyword, "Can't return a value from an initializer.")

            self.resolve_(stmt.value)

        return None

    def visit_while_stmt(self, stmt):
        self.resolve_(stmt.condition)
        self.resolve_(stmt.body)
        return None 

    def visit_binary_expr(self, expr):
        self.resolve_(expr.left)
        self.resolve_(expr.right)
        return None 

    def visit_call_expr(self, expr):
        self.resolve_(expr.callee)

        for argument in expr.arguments:
            self.resolve_(argument)

        return None
    
    def visit_get_expr(self, expr):
        self.resolve_(expr.object)
        return None

    def visit_set_expr(self, expr):
        self.resolve_(expr.value)
        self.resolve_(expr.object)
        return None

    def visit_grouping_expr(self, expr):
        self.resolve_(expr.expression)
        return None 

    def visit_literal_expr(self, expr):
        pass 

    def visit_logical_expr(self, expr):
        self.resolve_(expr.left)
        self.resolve_(expr.right)
        return None 

    def visit_unary_expr(self, expr):
        self.resolve_(expr.right)
        return None 

    def visit_self_expr(self, expr):
        if self.current_class == ClassType.NONE:
            Lox.error(expr.keyword, "Can't use 'self' outside of a class.")
            return 

        self.resolve_local(expr, expr.keyword)
        return 

    def visit_super_expr(self, expr):
        if self.current_class == ClassType.NONE:
            Lox.error(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            Lox.error(expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)
