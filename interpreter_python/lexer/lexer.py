from monkey_token.token import * 
from monkey_token.token_type import TokenType

# helper functions 
def is_letter(ch):
    return ('a' <= ch <= 'z') or ('A' <= ch <= 'Z') or (ch == '_')

def is_digit(ch):
    return '0' <= ch <= '9'

class Lexer:
    def __init__(self, input_str:str):
        self.input = input_str # full src code as a string 
        self.position = 0 # current pos in input (points to current char)
        self.read_position = 0 # current reading position in input
        self.ch = ''# current character under examination
        self.read_char()  # initialize the lexer by reading the first character

    def read_char(self):
        """Advance to the next char in input"""
        if self.read_position >= len(self.input):
            self.ch = '\0' # ASCII code for "NULL", signals end of input
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position +=1 
    
    def peek_char(self):
        """Returns the next character without moving the position"""
        if self.read_position >= len(self.input):
            return "\0"
        else:
            return self.input[self.read_position]
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines and carriage returns"""
        while self.ch in (' ', '\t', '\n', '\r'):
            self.read_char()
    
    def next_token(self):
        """Return the next token from the input"""
        self.skip_whitespace()

        # Default token initialization
        tok = None 
        
        if self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch 
                self.read_char()
                literal = ch + self.ch
                tok = Token(TokenType.EQ, literal)
            else:
                tok = Token(TokenType.ASSIGN, self.ch)
        elif self.ch == '+':
            tok = Token(TokenType.PLUS, self.ch)
        elif self.ch == '-':
            tok = Token(TokenType.MINUS, self.ch)
        elif self.ch =='!':
            if self.peek_char() == '=':
                ch = self.ch 
                self.read_char()
                literal = ch + self.ch 
                tok = Token(TokenType.NOT_EQ, literal)
            else:
                tok = Token(TokenType.BANG, self.ch)
        elif self.ch == '/':
            tok = Token(TokenType.SLASH, self.ch)
        elif self.ch == '*':
            tok = Token(TokenType.ASTERISK, self.ch)
        elif self.ch == '<':
            tok = Token(TokenType.LT, self.ch)
        elif self.ch == '>':
            tok = Token(TokenType.GT, self.ch)
        elif self.ch == ';':
            tok = Token(TokenType.SEMICOLON, self.ch)
        elif self.ch == '(':
            tok = Token(TokenType.LPAREN, self.ch)
        elif self.ch == ')':
            tok = Token(TokenType.RPAREN, self.ch)
        elif self.ch == ',':
            tok = Token(TokenType.COMMA, self.ch)
        elif self.ch == '{':
            tok = Token(TokenType.LBRACE, self.ch)
        elif self.ch == '}':
            tok = Token(TokenType.RBRACE, self.ch)
        elif self.ch == '\0':
            tok = Token(TokenType.EOF, '')
        else:
            if is_letter(self.ch):
                literal = self.read_identifer()
                token_type = lookup_ident(literal)
                return Token(token_type, literal)
            elif is_digit(self.ch):
                literal = self.read_number()
                return Token(TokenType.INT, literal)
            else:
                tok = Token(TokenType.ILLEGAL, self.ch)
        
        self.read_char()
        return tok 

    def read_identifer(self):
        """Read a sequence of letters and underscores as an identifier"""
        start_pos = self.position 
        while is_letter(self.ch):
            self.read_char()
        return self.input[start_pos: self.position]

    def read_number(self):
        """Read a sequenc of digits as a number"""
        start_pos = self.position
        while is_digit(self.ch):
            self.read_char()
        return self.input[start_pos:self.position]
