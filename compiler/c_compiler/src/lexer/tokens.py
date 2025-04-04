from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Any

class TokenType(Enum):
    # Keywords
    INT = auto()
    CHAR = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    
    # Operators
    PLUS = auto()          # +
    MINUS = auto()         # -
    STAR = auto()          # *
    SLASH = auto()         # /
    ASSIGN = auto()        # =
    EQUALS = auto()        # ==
    NOT_EQUALS = auto()    # !=
    LESS = auto()          # <
    GREATER = auto()       # >
    LESS_EQUALS = auto()   # <=
    GREATER_EQUALS = auto()# >=
    
    # Delimiters
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    SEMICOLON = auto()     # ;
    COMMA = auto()         # ,
    
    # Literals
    INTEGER = auto()       # 123
    STRING = auto()        # "hello"
    IDENTIFIER = auto()    # variable names
    
    # Special
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: Optional[Any] = None
    line: int = 0
    column: int = 0
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.column})" 