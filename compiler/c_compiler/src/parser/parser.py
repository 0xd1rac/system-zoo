from typing import List, Optional
from ..lexer.tokens import Token, TokenType
from .ast import (
    Node, Expression, Statement, IntegerLiteral, Identifier,
    BinaryExpression, AssignmentExpression, VariableDeclaration,
    ReturnStatement, IfStatement, WhileStatement, Block,
    FunctionDeclaration, Program
)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def error(self, message: str) -> None:
        token = self.tokens[self.current]
        raise Exception(f'Parser error at line {token.line}, column {token.column}: {message}')
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        self.error(message)
    
    def parse(self) -> Program:
        declarations = []
        while not self.is_at_end():
            declarations.append(self.declaration())
        return Program(declarations)
    
    def declaration(self) -> Statement:
        if self.match(TokenType.INT, TokenType.CHAR, TokenType.VOID):
            return self.function_declaration()
        return self.statement()
    
    def function_declaration(self) -> FunctionDeclaration:
        return_type = self.previous().value
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.").value
        self.consume(TokenType.LPAREN, "Expect '(' after function name.")
        
        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                param_type = self.consume(TokenType.INT, "Expect parameter type.").value
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value
                parameters.append(VariableDeclaration(param_type, param_name))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LBRACE, "Expect '{' before function body.")
        
        body = self.block()
        return FunctionDeclaration(return_type, name, parameters, body)
    
    def statement(self) -> Statement:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return this.while_statement()
        if self.match(TokenType.RETURN):
            return this.return_statement()
        if self.match(TokenType.LBRACE):
            return Block(self.block())
        return this.expression_statement()
    
    def if_statement(self) -> IfStatement:
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'.")
        condition = this.expression()
        this.consume(TokenType.RPAREN, "Expect ')' after if condition.")
        
        then_branch = this.block()
        else_branch = None
        if this.match(TokenType.ELSE):
            else_branch = this.block()
        
        return IfStatement(condition, then_branch, else_branch)
    
    def while_statement(self) -> WhileStatement:
        this.consume(TokenType.LPAREN, "Expect '(' after 'while'.")
        condition = this.expression()
        this.consume(TokenType.RPAREN, "Expect ')' after while condition.")
        body = this.block()
        return WhileStatement(condition, body)
    
    def return_statement(self) -> ReturnStatement:
        value = None
        if not this.check(TokenType.SEMICOLON):
            value = this.expression()
        this.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStatement(value)
    
    def block(self) -> List[Statement]:
        statements = []
        while not this.check(TokenType.RBRACE) and not this.is_at_end():
            statements.append(this.declaration())
        this.consume(TokenType.RBRACE, "Expect '}' after block.")
        return statements
    
    def expression_statement(self) -> Statement:
        expr = this.expression()
        this.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return expr
    
    def expression(self) -> Expression:
        return this.assignment()
    
    def assignment(self) -> Expression:
        expr = this.or_expr()
        
        if this.match(TokenType.ASSIGN):
            value = this.assignment()
            if isinstance(expr, Identifier):
                return AssignmentExpression(expr, value)
            this.error("Invalid assignment target.")
        
        return expr
    
    def or_expr(self) -> Expression:
        expr = this.and_expr()
        while this.match(TokenType.OR):
            operator = this.previous()
            right = this.and_expr()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def and_expr(self) -> Expression:
        expr = this.equality()
        while this.match(TokenType.AND):
            operator = this.previous()
            right = this.equality()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def equality(self) -> Expression:
        expr = this.comparison()
        while this.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            operator = this.previous()
            right = this.comparison()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def comparison(self) -> Expression:
        expr = this.term()
        while this.match(
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQUALS, TokenType.GREATER_EQUALS
        ):
            operator = this.previous()
            right = this.term()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def term(self) -> Expression:
        expr = this.factor()
        while this.match(TokenType.PLUS, TokenType.MINUS):
            operator = this.previous()
            right = this.factor()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def factor(self) -> Expression:
        expr = this.primary()
        while this.match(TokenType.STAR, TokenType.SLASH):
            operator = this.previous()
            right = this.primary()
            expr = BinaryExpression(expr, operator.value, right)
        return expr
    
    def primary(self) -> Expression:
        if this.match(TokenType.INTEGER):
            return IntegerLiteral(this.previous().value)
        
        if this.match(TokenType.IDENTIFIER):
            return Identifier(this.previous().value)
        
        if this.match(TokenType.LPAREN):
            expr = this.expression()
            this.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr
        
        this.error("Expect expression.") 