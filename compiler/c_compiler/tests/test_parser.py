import pytest
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.parser.ast import (
    Program, FunctionDeclaration, Block, ReturnStatement,
    IntegerLiteral, VariableDeclaration, BinaryExpression,
    Identifier, IfStatement, WhileStatement
)

def test_parse_simple_function():
    source = """
    int main() {
        return 42;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.declarations) == 1
    
    func = ast.declarations[0]
    assert isinstance(func, FunctionDeclaration)
    assert func.return_type == "int"
    assert func.name == "main"
    assert len(func.parameters) == 0
    
    body = func.body
    assert isinstance(body, Block)
    assert len(body.statements) == 1
    
    ret_stmt = body.statements[0]
    assert isinstance(ret_stmt, ReturnStatement)
    assert isinstance(ret_stmt.value, IntegerLiteral)
    assert ret_stmt.value.value == 42

def test_parse_variable_declaration():
    source = """
    int x = 10;
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.declarations) == 1
    
    var_decl = ast.declarations[0]
    assert isinstance(var_decl, VariableDeclaration)
    assert var_decl.type == "int"
    assert var_decl.name == "x"
    assert isinstance(var_decl.initializer, IntegerLiteral)
    assert var_decl.initializer.value == 10

def test_parse_if_statement():
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
    
    assert isinstance(ast, Program)
    assert len(ast.declarations) == 1
    
    if_stmt = ast.declarations[0]
    assert isinstance(if_stmt, IfStatement)
    
    condition = if_stmt.condition
    assert isinstance(condition, BinaryExpression)
    assert condition.operator == ">"
    assert isinstance(condition.left, Identifier)
    assert condition.left.name == "x"
    assert isinstance(condition.right, IntegerLiteral)
    assert condition.right.value == 0
    
    assert isinstance(if_stmt.then_branch, Block)
    assert len(if_stmt.then_branch.statements) == 1
    assert isinstance(if_stmt.else_branch, Block)
    assert len(if_stmt.else_branch.statements) == 1

def test_parse_while_statement():
    source = """
    while (x > 0) {
        x = x - 1;
    }
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.declarations) == 1
    
    while_stmt = ast.declarations[0]
    assert isinstance(while_stmt, WhileStatement)
    
    condition = while_stmt.condition
    assert isinstance(condition, BinaryExpression)
    assert condition.operator == ">"
    assert isinstance(condition.left, Identifier)
    assert condition.left.name == "x"
    assert isinstance(condition.right, IntegerLiteral)
    assert condition.right.value == 0
    
    assert isinstance(while_stmt.body, Block)
    assert len(while_stmt.body.statements) == 1 