from token_type import TokenType

keywords = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN
}

def lookup_ident(ident: str) -> TokenType:
    return keywords.get(ident, TokenType.IDENT)


