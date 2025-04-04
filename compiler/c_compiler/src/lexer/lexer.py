from typing import List, Optional
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source[0] if source else None
        
        # Keywords mapping
        self.keywords = {
            'int': TokenType.INT,
            'char': TokenType.CHAR,
            'void': TokenType.VOID,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
        }
    
    def error(self, message: str) -> None:
        raise Exception(f'Lexer error at line {self.line}, column {self.column}: {message}')
    
    def advance(self) -> None:
        """Advance the position pointer and set the current_char."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        
        self.position += 1
        self.column += 1
        
        if self.position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.position]
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip single-line comments."""
        while self.current_char and self.current_char != '\n':
            self.advance()
    
    def number(self) -> Token:
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        return Token(TokenType.INTEGER, int(result), self.line, self.column)
    
    def identifier(self) -> Token:
        """Handle identifiers and keywords."""
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, self.line, self.column)
    
    def get_next_token(self) -> Token:
        """Lexical analyzer (tokenizer)"""
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '/' and self.peek() == '/':
                self.advance()  # consume first '/'
                self.advance()  # consume second '/'
                self.skip_comment()
                continue
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Single-character tokens
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column)
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column)
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.STAR, '*', self.line, self.column)
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.SLASH, '/', self.line, self.column)
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column)
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column)
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column)
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column)
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column)
            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column)
            
            # Two-character tokens
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()  # consume first '='
                    self.advance()  # consume second '='
                    return Token(TokenType.EQUALS, '==', self.line, self.column)
                self.advance()
                return Token(TokenType.ASSIGN, '=', self.line, self.column)
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()  # consume '!'
                    self.advance()  # consume '='
                    return Token(TokenType.NOT_EQUALS, '!=', self.line, self.column)
                self.error('Expected != after !')
            
            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()  # consume '<'
                    self.advance()  # consume '='
                    return Token(TokenType.LESS_EQUALS, '<=', self.line, self.column)
                self.advance()
                return Token(TokenType.LESS, '<', self.line, self.column)
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()  # consume '>'
                    self.advance()  # consume '='
                    return Token(TokenType.GREATER_EQUALS, '>=', self.line, self.column)
                self.advance()
                return Token(TokenType.GREATER, '>', self.line, self.column)
            
            self.error(f'Invalid character: {self.current_char}')
        
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def peek(self) -> Optional[str]:
        """Look at the next character without consuming it."""
        peek_pos = self.position + 1
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def tokenize(self) -> List[Token]:
        """Return all tokens from the input."""
        tokens = []
        while True:
            token = this.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens 