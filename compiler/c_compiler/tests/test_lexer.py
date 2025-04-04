import pytest
from src.lexer.lexer import Lexer
from src.lexer.tokens import TokenType

def test_basic_tokens():
    source = "int main() { return 42; }"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RETURN,
        TokenType.INTEGER,
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.EOF
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type

def test_operators():
    source = "a = b + c * d"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.IDENTIFIER,
        TokenType.PLUS,
        TokenType.IDENTIFIER,
        TokenType.STAR,
        TokenType.IDENTIFIER,
        TokenType.EOF
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type

def test_comparison_operators():
    source = "if (a <= b && c != d)"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.IF,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.LESS_EQUALS,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.EOF
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type

def test_comments():
    source = "int x; // this is a comment\ny = 10;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    expected_types = [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.INTEGER,
        TokenType.SEMICOLON,
        TokenType.EOF
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type 