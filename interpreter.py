from visitor import *
from Token import *
from tokentype import TokenType
from runtime_error import RuntimeError_
from error_handler import ErrorHandler
from Expr import Expr
from Stmt import Stmt 

class Interpreter(Visitor):
    def __init__(self):
        self.error_handler = ErrorHandler()

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)
    
    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        stmt.accept(self)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator ==  TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        
        elif expr.operator ==  TokenType.BANG:
            return not self.is_truthy(right)

        return None 

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
            raise RuntimeError_(expr.operator, "Operands must be two numbers or two strings.")
        
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

    def is_truthy(self, object):
        if object is None: return False
        if (isinstance(object, bool)): return bool(object)
        return True 

    def check_number_operand(self, operator, left, right):
        if (isinstance(left, float) and isinstance(right, float)): return 
        raise RuntimeError_(operator, "Operand must be a number.")

    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError_ as e:
            self.error_handler.runtime_error(e)

    def stringify(self, object):
        if object is None:
            return "nil"
        else:
            return str(object)
