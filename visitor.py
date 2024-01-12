from Expr import *
from abc import ABC, abstractmethod
from token import *


class Visitor(ABC):
    @abstractmethod
    def visitBinaryExpr(self, expr:  Binary):
        pass

    @abstractmethod
    def visitGroupingExpr(self, expr:  Grouping):
        pass

    @abstractmethod
    def visitLiteralExpr(self, expr:  Literal):
        pass

    @abstractmethod
    def visitUnaryExpr(self, expr:  Unary):
        pass

