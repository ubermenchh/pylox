from Stmt import *
from abc import ABC, abstractmethod
from token import *


class Visitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt:  Expression):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt:  Print):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt:  Var):
        pass

