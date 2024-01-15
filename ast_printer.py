from Expr import Expr
from visitor import *
from Token import *
from tokentype import TokenType


class AstPrinter(Visitor):
    def __init__(self):
        pass

    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value == None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_print_stmt(self, stmt):
        return None

    def visit_expression_stmt(self, stmt):
        return None

    def parenthesize(self, name, exprs):
        res = f"({name}"
        for expr in exprs:
            res += f" {expr.accept(self)}"
        res += ")"
        return res


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    printer = AstPrinter()
    print(printer.print(expression))
