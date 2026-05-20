from typing import Optional, Set, List
from .jack_token import JackToken
from .token_type import TokenType


class Tokenizer:
    """
    Tokenizer for Jack language.

    Breaks the input text into tokens for the parser.
    """

    KEYWORDS: Set[str] = {
        "class", "constructor", "function", "method", "field", "static", "var",
        "int", "char", "boolean", "void", "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return"
    }

    SYMBOLS: Set[str] = set('{}()[].,;+-*/&|<>=~')

    def __init__(self, text: str):
        """
        Initialize the tokenizer with input text.

        Args:
            text: The Jack source code to tokenize
        """
        self.text = text
        self.pos = 0
        self.prev_tokens: List[JackToken] = []
        self.line_number = 1
        self.col_number = 1
        self.start_line_number = 0
        self.start_col_number = 0

    @property
    def ch(self) -> str:
        """Get the current character."""
        if self.pos >= len(self.text):
            return ''
        return self.text[self.pos]

    def _advance(self) -> str:
        """Advance position by one character, tracking line/col."""
        c = self.ch
        if c == '\n':
            self.line_number += 1
            self.col_number = 1
        else:
            self.col_number += 1
        self.pos += 1
        return c

    def try_read_next(self) -> Optional[JackToken]:
        """
        Read the next token from the input.

        Returns tokens pushed back with push_back() in LIFO order first,
        then reads and returns the next token from the input.
        Skips whitespace and comments.

        Returns:
            The next JackToken or None if there are no more tokens
        """
        if self.prev_tokens:
            return self.prev_tokens.pop()

        while True:
            while self.ch and self.ch.isspace():
                self._advance()
            
            if not self.ch:
                return None

            if self.ch == '/' and self.pos + 1 < len(self.text):
                next_char = self.text[self.pos + 1]
                if next_char == '/':  
                    self._advance()  
                    self._advance()  
                    while self.ch and self.ch != '\n':
                        self._advance()
                    continue  
                elif next_char == '*':  
                    self._advance()  
                    self._advance()  
                    while self.ch:
                        if self.ch == '*' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/':
                            self._advance()  
                            self._advance() 
                            break
                        self._advance()
                    continue  
            break

        start_line = self.line_number
        start_col = self.col_number
        char = self.ch

        if char in self.SYMBOLS:
            self._advance()
            return JackToken(TokenType.SYMBOL, char, start_line, start_col)

        if char == '"':
            self._advance() 
            value = ""
            while self.ch and self.ch != '"':
                value += self.ch
                self._advance()
            if self.ch == '"':
                self._advance()  
            return JackToken(TokenType.STRING_CONSTANT, value, start_line, start_col)

        if char.isdigit():
            value = ""
            while self.ch and self.ch.isdigit():
                value += self.ch
                self._advance()
            return JackToken(TokenType.INTEGER_CONSTANT, value, start_line, start_col)

        if char.isalpha() or char == '_':
            value = ""
            while self.ch and (self.ch.isalnum() or self.ch == '_'):
                value += self.ch
                self._advance()
            
            if value in self.KEYWORDS:
                return JackToken(TokenType.KEYWORD, value, start_line, start_col)
            else:
                return JackToken(TokenType.IDENTIFIER, value, start_line, start_col)

        self._advance()
        return None

    def push_back(self, token: JackToken) -> None:
        """
        Push a token back to be read again.

        Args:
            token: The token to push back
        """
        self.prev_tokens.append(token)