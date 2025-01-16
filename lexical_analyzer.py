# lexical_analyzer.py
from enum import Enum
from typing import List, Dict, Optional, Set
import re

class TokenType(Enum):
    # Single characters
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    COMMA = ','
    SEMICOLON = ';'
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    SLASH = '/'
    PERCENT = '%'
    LESS = '<'
    GREATER = '>'
    EQUAL = '='
    BANG = '!'
    LBRACKET = '['
    RBRACKET = ']'
    
    # Double characters
    LE = '<='
    GE = '>='
    EQ = '=='
    NE = '!='
    OR = '||'
    AND = '&&'
    
    # Keywords
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    FOR = 'for'
    RETURN = 'return'
    BREAK = 'break'
    NEW = 'new'
    SIZE = 'size'
    
    # Types
    VOID = 'void'
    BOOL = 'bool'
    INT = 'int'
    FLOAT = 'float'
    
    # Literals and Identifier
    BOOL_LIT = 'BOOL_LIT'
    INT_LIT = 'INT_LIT'
    FLOAT_LIT = 'FLOAT_LIT'
    IDENTIFIER = 'IDENTIFIER'
    
    # End of file
    EOF = 'EOF'

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self): # ????
        return f"Token(type={self.type.name}, value='{self.value}', line={self.line}, column={self.column})"

class SymbolInfo:
    def __init__(self, name: str, type_: str, is_local: bool = True):
        self.name = name
        self.type = type_
        self.is_local = is_local
        self.array_length = -1  # -1 for non-arrays
        self.return_type = None  # for functions
        self.param_types = []    # for functions
        self.local_var_count = 0 # for functions

class SymbolTable:
    def __init__(self, name: str):
        self.symbols: Dict[str, SymbolInfo] = {}
        self.parent = None
        self.name = name
    
    def insert(self, name: str, info: SymbolInfo):
        self.symbols[name] = info
    
    def lookup(self, name: str) -> Optional[SymbolInfo]: # ????
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def print_table(self): # should we print the symbol table?
        print(f"\nSymbol Table for scope: {self.name}")
        print("-" * 50)
        for name, info in self.symbols.items():
            print(f"Name: {name:<15} Type: {info.type:<10} Local: {info.is_local}")

class LexicalError(Exception):
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")

class LexicalAnalyzer:
    KEYWORDS = {
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'return': TokenType.RETURN,
        'break': TokenType.BREAK,
        'new': TokenType.NEW,
        'size': TokenType.SIZE,
        'void': TokenType.VOID,
        'bool': TokenType.BOOL,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'true': TokenType.BOOL_LIT,
        'false': TokenType.BOOL_LIT
    }
    
    OPERATORS = {
        '<=': TokenType.LE,
        '>=': TokenType.GE,
        '==': TokenType.EQ,
        '!=': TokenType.NE,
        '||': TokenType.OR,
        '&&': TokenType.AND
    }

    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.symbol_table = SymbolTable("global")
        self.initialize_built_in_functions()

    def initialize_built_in_functions(self):
        # Add read function
        read_info = SymbolInfo("read", "function")
        read_info.return_type = "any"
        read_info.param_types = ["void"]
        self.symbol_table.insert("read", read_info)

        # Add write function
        write_info = SymbolInfo("write", "function")
        write_info.return_type = "void"
        write_info.param_types = ["any"]
        self.symbol_table.insert("write", write_info)

    def analyze(self) -> List[Token]:
        while True:
            token = self.next_token()
            self.tokens.append(token)
            if token.type == TokenType.EOF:
                break
            print(token)
        
        self.symbol_table.print_table()
        return self.tokens

    def next_token(self) -> Token:
        self.skip_whitespace()
        
        if self.position >= len(self.source):
            return Token(TokenType.EOF, "", self.line, self.column)

        char = self.source[self.position]

        # Handle comments
        if char == '/':
            if self.position + 1 < len(self.source):
                next_char = self.source[self.position + 1]
                if next_char == '/':
                    self.skip_line_comment()
                    return self.next_token()
                elif next_char == '*':
                    self.skip_block_comment()
                    return self.next_token()

        # Handle numbers
        if char.isdigit():
            return self.scan_number()

        # Handle identifiers and keywords
        if char.isalpha() or char == '_':
            return self.scan_identifier()

        # Handle operators and punctuation
        if self.position + 1 < len(self.source):
            op = self.source[self.position:self.position + 2]
            if op in self.OPERATORS:
                self.position += 2
                self.column += 2
                return Token(self.OPERATORS[op], op, self.line, self.column - 2)

        # Single character tokens
        self.position += 1
        self.column += 1
        for token_type in TokenType:
            if token_type.value == char:
                return Token(token_type, char, self.line, self.column - 1)

        raise LexicalError(f"Unexpected character: {char}", self.line, self.column - 1)

    def skip_whitespace(self):
        while self.position < len(self.source) and self.source[self.position].isspace():
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def skip_line_comment(self):
        self.position += 2  # Skip //
        while self.position < len(self.source) and self.source[self.position] != '\n':
            self.position += 1

    def skip_block_comment(self):
        self.position += 2  # Skip /*
        while self.position < len(self.source) - 1:
            if (self.source[self.position] == '*' and 
                self.source[self.position + 1] == '/'):
                self.position += 2
                return
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
        raise LexicalError("Unterminated block comment", self.line, self.column)

    def scan_number(self) -> Token:
        start_column = self.column
        number = ""
        is_float = False
        
        while self.position < len(self.source):
            char = self.source[self.position]
            if char.isdigit():
                number += char
                self.position += 1
                self.column += 1
            elif char == '.' and not is_float:
                number += char
                is_float = True
                self.position += 1
                self.column += 1
            else:
                break

        if is_float:
            if number.endswith('.'):
                raise LexicalError("Invalid float literal", self.line, start_column)
            return Token(TokenType.FLOAT_LIT, number, self.line, start_column)
        return Token(TokenType.INT_LIT, number, self.line, start_column)

    def scan_identifier(self) -> Token:
        start_column = self.column
        identifier = ""
        
        while self.position < len(self.source):
            char = self.source[self.position]
            if char.isalnum() or char == '_':
                identifier += char
                self.position += 1
                self.column += 1
            else:
                break

        # Check if it's a keyword
        if identifier in self.KEYWORDS:
            return Token(self.KEYWORDS[identifier], identifier, self.line, start_column)

        # Add to symbol table if it's an identifier
        if not self.symbol_table.lookup(identifier):
            self.symbol_table.insert(identifier, SymbolInfo(identifier, "unknown"))

        return Token(TokenType.IDENTIFIER, identifier, self.line, start_column)

# Example usage and test
def main():
    # Test the lexical analyzer with a sample MyC program
    sample_program = """
    int main() {
        float x = .14;
        // This is a comment
        if (x <= 5.0) {
            /* Multi-line
               comment */
            return 0;
        }
        return 1;
    }
    """
    
    try:
        lexer = LexicalAnalyzer(sample_program)
        tokens = lexer.analyze()
    except LexicalError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
