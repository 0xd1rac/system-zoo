from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Node:
    """Base class for all AST nodes"""
    pass

@dataclass
class Expression(Node):
    """Base class for all expressions"""
    pass

@dataclass
class Statement(Node):
    """Base class for all statements"""
    pass

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class AssignmentExpression(Expression):
    left: Identifier
    right: Expression

@dataclass
class VariableDeclaration(Statement):
    type: str
    name: str
    initializer: Optional[Expression] = None

@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression] = None

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_branch: 'Block'
    else_branch: Optional['Block'] = None

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: 'Block'

@dataclass
class Block(Statement):
    statements: List[Statement]

@dataclass
class FunctionDeclaration(Statement):
    return_type: str
    name: str
    parameters: List[VariableDeclaration]
    body: Block

@dataclass
class Program(Node):
    declarations: List[Union[FunctionDeclaration, VariableDeclaration]] 