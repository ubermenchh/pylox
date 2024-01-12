from Expr import *
from visitor import *
from token import *
from tokentype import *

class AstPrinter(Visitor):
    def print(expr):
        return expr.accept(self)

    def visit_binary_expr(expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(expr):
        if (expr.value == None): return "nil"
        return str(expr.value)

    def visit_unary_expr(expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(name, exprs):
        res = f"({name}"
        for expr in exprs:
            res += f" {expr.accept(self)}"
        res += ")"
        return res 

if __name__=="__main__":
    expression = Binary(
            Unary(
                Token(TokenType.MINUS, "-", None, 1),
                Literal(123)
                ),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(Literal(45.67))
            )
    printer = AstPrinter()
    print(printer.print(expression))
