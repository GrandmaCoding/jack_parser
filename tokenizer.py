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
        raise NotImplementedError()

    def push_back(self, token: JackToken) -> None:
        """
        Push a token back to be read again.

        Args:
            token: The token to push back
        """
        raise NotImplementedError()
