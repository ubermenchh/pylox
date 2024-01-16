from Stmt import *
from abc import ABC, abstractmethod
from token import *


class Visitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt:  Block):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt:  Expression):
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt:  Print):
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt:  Var):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt:  If):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt:  While):
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt:  Function):
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt:  Return):
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt:  Class):
        pass

