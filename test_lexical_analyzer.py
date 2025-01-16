# test_lexical_analyzer.py
import unittest
from lexical_analyzer import TokenType, LexicalAnalyzer, LexicalError


class TestLexicalAnalyzer(unittest.TestCase):
    def test_basic_program(self):
        source = "int main() { return 0; }"
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        self.assertEqual(tokens[0].type, TokenType.INT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "main")
        self.assertEqual(tokens[2].type, TokenType.LPAREN)

    def test_numbers(self):
        source = "123 45.67"
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        self.assertEqual(tokens[0].type, TokenType.INT_LIT)
        self.assertEqual(tokens[0].value, "123")
        self.assertEqual(tokens[1].type, TokenType.FLOAT_LIT)
        self.assertEqual(tokens[1].value, "45.67")

    def test_comments(self):
        source = """// Line comment
        int x; /* Block comment */ int y;"""
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        # Comments should be ignored
        self.assertEqual(tokens[0].type, TokenType.INT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[3].type, TokenType.INT)

    def test_operators(self):
        source = "x <= y >= z == w != v && k || m"
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        operator_types = [
            TokenType.IDENTIFIER, TokenType.LE, TokenType.IDENTIFIER,
            TokenType.GE, TokenType.IDENTIFIER, TokenType.EQ,
            TokenType.IDENTIFIER, TokenType.NE, TokenType.IDENTIFIER,
            TokenType.AND, TokenType.IDENTIFIER, TokenType.OR,
            TokenType.IDENTIFIER
        ]

        for token, expected_type in zip(tokens, operator_types):
            self.assertEqual(token.type, expected_type)

    def test_invalid_character(self):
        source = "int x = @;"
        lexer = LexicalAnalyzer(source)
        with self.assertRaises(LexicalError):
            lexer.analyze()

    def test_unterminated_comment(self):
        source = "/* This comment never ends"
        lexer = LexicalAnalyzer(source)
        with self.assertRaises(LexicalError):
            lexer.analyze()

    # def test_invalid_float(self):
    #     source = "123."
    #     lexer = LexicalAnalyzer(source)
    #     with self.assertRaises(LexicalError):
    #         lexer.analyze()
    #
    #     self.assertEqual(tokens[1].value, "45.67")

    def test_keywords_and_identifiers(self):
        source = "if else while x123 _testVar"
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        self.assertEqual(tokens[0].type, TokenType.IF)
        self.assertEqual(tokens[1].type, TokenType.ELSE)
        self.assertEqual(tokens[2].type, TokenType.WHILE)
        self.assertEqual(tokens[3].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[3].value, "x123")
        self.assertEqual(tokens[4].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[4].value, "_testVar")

    def test_comments(self):
        source = """
        // Single-line comment
        int x = 10; /* Multi-line
        comment */ return x;
        """
        lexer = LexicalAnalyzer(source)
        tokens = lexer.analyze()

        self.assertEqual(tokens[0].type, TokenType.INT)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.EQUAL)
        self.assertEqual(tokens[3].type, TokenType.INT_LIT)
        self.assertEqual(tokens[4].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[5].type, TokenType.RETURN)
        self.assertEqual(tokens[6].type, TokenType.IDENTIFIER)

    def test_unterminated_block_comment(self):
        source = "/* This is an unterminated comment"
        lexer = LexicalAnalyzer(source)
        with self.assertRaises(LexicalError):
            lexer.analyze()

    def test_invalid_character(self):
        source = "@"
        lexer = LexicalAnalyzer(source)
        with self.assertRaises(LexicalError):
            lexer.analyze()


if __name__ == '__main__':
    unittest.main()
