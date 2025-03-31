from monkey_token.token_type import TokenType
from monkey_token.token import Token
from typing import List 
from __future__ import annotations

class Node:
    def token_literal(self) -> str:
        raise NotImplementedError("token_literal() must be implemented by subclasses.")
    
class Statement(Node):
    def statement_node(self) -> None:
        """A marker method for statement nodes"""
        raise NotImplementedError("statement_node() must be implemented by subclasses")
    
class Expression(Node):
    def expression_node(self) -> None:
        """A marker method for expression nodes."""
        raise NotImplementedError("expression_node() must be implemented by subclasses")

class Program(Node):
    def __init__(self) -> None:
        # A list to hold Statement instances.
        self.statements = []
    
    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()
        return ""

class Identifier(Expression):
    def __init__(self, token: Token, value: str) -> None:
        """
        :param token: The token representing an identifier (should be token.IDENT)
        :param value: The actual identifier name.
        """
        self.token: Token = token
        self.value: str = value

    def expression_node(self) -> None:
        # marker moethod to differentiate expressions.
        pass 

    def token_literal(self) -> str:
        return self.token.literal

class LetStatement(Statement):
    def __init__(self, token:Token, name: Identifier, value: Expression) -> None:
        """
        :param token: The token representing 'LET'
        :param name: An Identifier instance representing the variable name.
        :param value: An Expression instance representing the assigned value.
        """
        self.token = token
        self.name = name 
        self.value = value 

    def statement_node(self) -> None:
        # marker method to differentiate statements
        pass 

    def token_literal(self) -> str:
        return self.token.literal
    

