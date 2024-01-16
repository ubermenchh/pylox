from visitor import *
from Token import *
from tokentype import TokenType
from runtime_error import RuntimeError_
from error_handler import ErrorHandler
from Expr import *
from Stmt import *
from Environment import Environment
from lox_callable import *
from lox_function import *
from Return import *
from lox_class import *
from lox_instance import *

from time import time


class Interpreter(Visitor):
    def __init__(self, error_handler):
        self.error_handler = error_handler
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

        class clock(LoxCallable):
            def __init__(self):
                super().__init__()
                self.start_time = time()

            def arity(self):
                return 0

            def call(self, Interpreter, arguments):
                return time() - self.start_time

            def __str__(self):
                return f"<Native Function 'clock'>"

        self.globals.define("clock", clock())


    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)

        if expr.operator == TokenType.BANG:
            return not self.is_truthy(right)

        return None

    def visit_variable_expr(self, expr):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        _type = expr.operator.tokentype
        if _type == TokenType.MINUS:
            self.check_number_operand(expr.operator, left, right)
            return float(left) - float(right)

        elif _type == TokenType.SLASH:
            self.check_number_operand(expr.operator, left, right)
            return float(left) / float(right)

        elif _type == TokenType.STAR:
            self.check_number_operand(expr.operator, left, right)
            return float(left) * float(right)

        elif _type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            elif isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise RuntimeError_(
                expr.operator, "Operands must be two numbers or two strings."
            )

        elif _type == TokenType.GREATER:
            self.check_number_operand(expr.operator, left, right)
            return float(left) > float(right)

        elif _type == TokenType.GREATER_EQUAL:
            self.check_number_operand(expr.operator, left, right)
            return float(left) >= float(right)

        elif _type == TokenType.LESS:
            self.check_number_operand(expr.operator, left, right)
            return float(left) < float(right)

        elif _type == TokenType.LESS_EQUAL:
            self.check_number_operand(expr.operator, left, right)
            return float(left) <= float(right)

        elif _type == TokenType.BANG_EQUAL:
            return not (left == right)

        elif _type == TokenType.EQUAL_EQUAL:
            return left == right

        return None

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_return_stmt(self, stmt):
        value = None 
        if stmt.value is not None:
            value = self.evaluate(stmt.value)

        raise Return(value)

    def visit_class_stmt(self, stmt):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError_(stmt.superclass.name, "Superclass must be a class.")

        self.environment.define(stmt.name.lexeme, None)

        if stmt.superclass is not None:
            environment = Environment(self.environment)
            environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, method.name.lexeme=="init")
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        
        if superclass is not None:
            environment.assign(stmt.name, klass)

        self.environment.assign(stmt.name, klass)

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        distance = self.locals.get(expr)

        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)

        if expr.operator.tokentype == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = []

        if not isinstance(callee, LoxCallable):
            raise RuntimeError_(expr.paren, "Can only call functions and classes.")

        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if callee.arity() != len(arguments):
            raise RuntimeError_(expr.paren_loc, f"Expected {callee.arity()} arguments but got {len(arguments)}")

        return callee.call(self, arguments)

    def visit_get_expr(self, expr):
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)

        raise RuntimeError_(expr.name, "Only instances have properties.")

    def visit_set_expr(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, LoxInstance):
            raise RuntimeError_(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        object.set(expr.name, value)

        return value

    def visit_self_expr(self, expr):
        return self.lookup_variable(expr.keyword, expr)

    def visit_super_expr(self, expr):
        distance = self.locals[expr]
        superclass = self.environment.get_at(distance, "super")
        object = self.environment.get_at(distance - 1, "self")
        method = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise RuntimeError_(expr.method, f"Undefined property '{expr.method.lexeme}' .")

        return method.bind(object)

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        else:
            return None

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def is_truthy(self, object):
        if object is None:
            return False
        if isinstance(object, bool):
            return bool(object)
        return True

    def check_number_operand(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise RuntimeError_(operator, "Operand must be a number.")

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError_ as e:
            self.error_handler.runtime_error(e)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def stringify(self, object):
        if object is None:
            return "nil"
        else:
            return str(object)
