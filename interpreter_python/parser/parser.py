from monkey_token.token import Token
from lexer.lexer import Lexer
from ast.ast import *


class Parser:
    def __init__(self, lexer:Lexer) -> None:
        self.l = lexer
        self.cur_token = None
        self.peek_token = None 

        # read two tokens so that cur_token and peek_token are both set
        self.next_token()
        self.next_token()

    def next_token(self) -> None:
        """Advance tokens: set cur_token to peek_token, and peek_token to the next token from the lexer."""
        self.cur_token = self.peek_token
        self.peek_token = self.l.next_token()
    
    def parse_program(self) -> Program:
        """Parses the entire program and returns an AST Program node"""
        
        
        return None 