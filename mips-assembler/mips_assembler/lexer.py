from dataclasses import dataclass
from typing import Iterator, List, Optional

@dataclass
class Token:
    """Represents a token in the MIPS assembly code"""
    type: str
    value: str
    line: int
    column: int

class LexerError(Exception):
    """Custom exception for lexer errors"""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")

class MIPSLexer:
    """Lexer for MIPS assembly code"""
    
    # List of known MIPS instructions
    INSTRUCTIONS = {
        'add', 'sub', 'and', 'or', 'slt', 'sll', 'srl', 'nop',
        'addi', 'lw', 'sw', 'beq', 'bne', 'j', 'jal'
    }
    
    def __init__(self):
        """Initialize the lexer"""
        pass

    def _is_whitespace(self, char: str) -> bool:
        """Check if a character is whitespace"""
        return char in ' \t\n\r'

    def _is_alpha(self, char: str) -> bool:
        """Check if a character is alphabetic"""
        return char.isalpha() or char == '_'

    def _is_alnum(self, char: str) -> bool:
        """Check if a character is alphanumeric"""
        return char.isalnum() or char == '_'

    def _is_digit(self, char: str) -> bool:
        """Check if a character is a digit"""
        return char.isdigit() or char == '-'

    def _get_next_token(self, text: str, pos: int, line: int) -> tuple[Optional[Token], int]:
        """
        Get the next token from the text starting at pos
        
        Args:
            text: The input text
            pos: Current position in the text
            line: Current line number
            
        Returns:
            Tuple of (Token, new_position) or (None, new_position) if no token found
        """
        # Skip whitespace
        while pos < len(text) and self._is_whitespace(text[pos]):
            if text[pos] == '\n':
                line += 1
            pos += 1
        
        if pos >= len(text):
            return None, pos
            
        char = text[pos]
        start_pos = pos
        
        # Handle comments
        if char == '#':
            while pos < len(text) and text[pos] != '\n':
                pos += 1
            return None, pos
            
        # Handle labels
        if self._is_alpha(char):
            while pos < len(text) and self._is_alnum(text[pos]):
                pos += 1
            if pos < len(text) and text[pos] == ':':
                return Token('LABEL', text[start_pos:pos], line, start_pos + 1), pos + 1
            value = text[start_pos:pos]
            if value in self.INSTRUCTIONS:
                return Token('INSTR', value, line, start_pos + 1), pos
            return Token('IDENT', value, line, start_pos + 1), pos
            
        # Handle registers
        if char == '$':
            pos += 1
            while pos < len(text) and self._is_alnum(text[pos]):
                pos += 1
            return Token('REG', text[start_pos:pos], line, start_pos + 1), pos
            
        # Handle numbers
        if self._is_digit(char):
            pos += 1
            while pos < len(text) and text[pos].isdigit():
                pos += 1
            return Token('NUM', text[start_pos:pos], line, start_pos + 1), pos
            
        # Handle single-character tokens
        if char == ',':
            return Token('COMMA', ',', line, start_pos + 1), pos + 1
        if char == '(':
            return Token('LPAREN', '(', line, start_pos + 1), pos + 1
        if char == ')':
            return Token('RPAREN', ')', line, start_pos + 1), pos + 1
            
        # If we get here, we have an invalid character
        raise LexerError(f"Invalid character: {char}", line, start_pos + 1)

    def tokenize(self, text: str) -> Iterator[Token]:
        """
        Tokenize the input text into a sequence of tokens
        
        Args:
            text: The input MIPS assembly code
            
        Yields:
            Token objects representing each token in the code
        """
        pos = 0
        line = 1
        
        while pos < len(text):
            token, pos = self._get_next_token(text, pos, line)
            if token:
                # Convert IDENT to LABEL if it's a branch target
                if token.type == 'IDENT' and token.value not in self.INSTRUCTIONS:
                    token = Token('LABEL', token.value, token.line, token.column)
                yield token
                if token.type == 'LABEL':
                    line = token.line

    def get_tokens(self, text: str) -> List[Token]:
        """
        Get all tokens from the input text as a list
        
        Args:
            text: The input MIPS assembly code
            
        Returns:
            List of Token objects
        """
        return list(self.tokenize(text))

# Example usage
if __name__ == '__main__':
    code = """
    loop:   add $t0, $t1, $t2   # This is a comment
            lw $s1, 0($sp)
            beq $t0, $zero, end
    end:    nop
    """
    
    lexer = MIPSLexer()
    tokens = lexer.get_tokens(code)
    
    for token in tokens:
        print(f"Type: {token.type:<10} Value: {token.value:<10} Line: {token.line} Column: {token.column}") 