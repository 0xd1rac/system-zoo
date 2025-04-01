from monkey_token.token import Token
from monkey_token.token_type import TokenType
from lexer.lexer import Lexer
from ast.ast import *
from ast.ast import Program, LetStatement, Identifier


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
        program = Program()
        while self.cur_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)

            self.next_token()
        return program
    
    def parse_statement(self):
        if self.cur_token.type == TokenType.LET:
            return self.parse_let_statement()
        return None 
    
    def parse_let_statement(self):
        stmt = LetStatement(token=self.cur_token, name=None, value=None)

        # Check that the next token is an identifier
        if self.peek_token.type != TokenType.IDENT:
            return None

        self.next_token() # Now cur_tk=oken is the identifier
        stmt.name = Identifier(token=self.cur_token, value=self.cur_token.literal)

        # Ensure the following token is an assignemnt operator, then advance 
        if self.peek_token.type != TokenType.ASSIGN:
            return None
        
        self.next_token()

        # Skip parinsg the expression until we encounter a semicolon
        while self.cur_token.type != TokenType.SEMICOLON:
            self.next_token()
        
        return stmt