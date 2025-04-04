import pytest
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.codegen.arm_generator import ARMGenerator

def test_simple_function():
    source = """
    int main() {
        return 42;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = ARMGenerator()
    assembly = generator.generate_program(ast)
    
    # Check for essential ARM assembly components
    assert ".data" in assembly
    assert ".text" in assembly
    assert ".global _start" in assembly
    assert "main:" in assembly
    assert "mov r4, #42" in assembly
    assert "mov r0, r4" in assembly
    assert "bx lr" in assembly

def test_variable_declaration():
    source = """
    int x = 10;
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = ARMGenerator()
    assembly = generator.generate_program(ast)
    
    assert "mov r4, #10" in assembly
    assert "str r4, [fp," in assembly

def test_if_statement():
    source = """
    if (x > 0) {
        return 1;
    } else {
        return 0;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = ARMGenerator()
    assembly = generator.generate_program(ast)
    
    assert "cmp r4, #0" in assembly
    assert "beq else" in assembly
    assert "mov r4, #1" in assembly
    assert "mov r4, #0" in assembly

def test_while_statement():
    source = """
    while (x > 0) {
        x = x - 1;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = ARMGenerator()
    assembly = generator.generate_program(ast)
    
    assert "while" in assembly
    assert "cmp r4, #0" in assembly
    assert "beq endwhile" in assembly
    assert "sub r4, r5, r6" in assembly
    assert "str r4, [fp," in assembly

def test_binary_operations():
    source = """
    int x = a + b * c;
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = ARMGenerator()
    assembly = generator.generate_program(ast)
    
    assert "add r4, r5, r6" in assembly
    assert "mul r4, r5, r6" in assembly
    assert "str r4, [fp," in assembly 