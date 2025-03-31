import sys 
from lexer.lexer import Lexer
from monkey_token.token_type import TokenType

PROMPT = ">>"
def start():
    while True:
        sys.stdout.write(PROMPT)
        sys.stdout.flush()  # Ensure the prompt is displayed immediately
        line = sys.stdin.readline()
        if not line:
            break # end of input stream
        line = line.rstrip("\n")

        lexer = Lexer(line)
        tok = lexer.next_token()
        while tok.type != TokenType.EOF:
            sys.stdout.write(f"{tok}\n")
            tok = lexer.next_token()
            
if __name__ == '__main__':
    start()