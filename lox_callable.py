from interpreter import * 
from abc import ABC, abstractmethod 

class LoxCallable:
    @abstractmethod
    def call(self, interpreter, arguments):
        pass

    @abstractmethod 
    def arity(self):
        pass 

    @abstractmethod 
    def __str__(self):
        pass
