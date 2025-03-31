import unittest 
from lexer.lexer import Lexer 
from parser.parser import Parser
from ast.ast import Program, Identifier, LetStatement

class TestLetStatements(unittest.TestCase):
    def test_let_statements(self) -> None:
        input_str = """
                    let x = 5;
                    let y = 10;
                    let foobar = 838383;
                    """
        lexer = Lexer(input_str)
        parser = Parser(lexer)

        program = parser.parse_program()

        # check that parse_program() returned a Program
        self.assertIsNotNone(program, "parse_program() returned None")
        self.assertEqual(len(program.statements), 3,
                         f"program.statements does not contain 3 statements. Got {len(program.statements)}")

        # Expected variable names in each let statement
        expected_identifiers = ["x", "y", "foobar"]

        for i, expected in enumerate(expected_identifiers):
            stmt = program.statements[i]
            self.assertTrue(test_let_statement(self, stmt, expected))
        

def test_let_statement(test_case: unittest.TestCase, s, expected_identifier: str) -> bool:
    # Check that the token literal of the statement is "let"
    test_case.assertEqual(s.token_literal(), "let",
                          f"s.token_literal() is not 'let'. Got {s.token_literal()}")
                          
    # Check that s is an instance of LetStatement 
    test_case.assertIsInstance(s, LetStatement, 
                               f"s is not an instance of LetStatement. Got {type(s)}")
    

    # Check that the identifer (variable name) is expected 
    test_case.assertEqual(s.name.value, expected_identifier,
                        f"LetStatement.name.value not '{expected_identifier}'. Got {s.name.value}")

    # Check that the identifier's token literal equals the expected identifier
    test_case.assertEqual(s.name.token_literal(), expected_identifier,
                          f"s.name.token_literal() not '{expected_identifier}'. Got {s.name.token_literal()}")
    
    return True

if __name__ == '__main__':
    unittest.main()