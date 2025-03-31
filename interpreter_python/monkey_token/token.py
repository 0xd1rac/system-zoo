from dataclasses import dataclass 
from .token_type import TokenType

class Token:
    def __init__(self, token_type: TokenType, literal:str):
        self.type = token_type
        self.literal = literal
    
    def __repr__(self):
        return f"Token({self.type}, {self.literal})"

# checks if an identifier is a reserved keyword; if not it's just an IDENT
def lookup_ident(ident: str) -> TokenType:
    keywords = {
        "fn": TokenType.FUNCTION,
        "let": TokenType.LET,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "return": TokenType.RETURN
    }
    
    return keywords.get(ident, TokenType.IDENT)


