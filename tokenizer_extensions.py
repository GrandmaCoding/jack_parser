from typing import TypeVar, Callable, List, Optional, Any
from .jack_token import JackToken
from .token_type import TokenType
from .tokenizer import Tokenizer
from .exceptions import ExpectedException


T = TypeVar('T')


def read(self, expected: str = None, token_type: TokenType = None) -> JackToken:
    """
    Read the next token and verify it matches the expected value or type.
    
    Args:
        expected: Optional expected value of the token
        token_type: Optional expected token type
        
    Returns:
        The token if it matches the expectations
        
    Raises:
        ValueError: If the token doesn't match expectations
    """
    token = self.try_read_next()
    
    if token is None:
        raise ValueError(f"Expected '{expected}' but got end of file")
        
    if expected is not None and token.value != expected:
        raise ValueError(f"Expected '{expected}' but got '{token.value}'")
        
    if token_type is not None and token.token_type != token_type:
        raise ValueError(f"Expected token type {token_type} but got {token.token_type}")
        
    return token


def read_list(self, item_parser: Callable[[JackToken], Optional[T]]) -> List[T]:
    """
    Read a list of items using the provided parser function.
    
    Continues reading items until the parser returns None.
    
    Args:
        item_parser: Function that parses a token into an item or returns None
        
    Returns:
        List of successfully parsed items
    """
    result: List[T] = []
    
    while True:
        token = self.try_read_next()
        if token is None:
            break
            
        item = item_parser(token)
        if item is None:
            self.push_back(token)
            break
            
        result.append(item)
        
    return result


def read_delimited_list(self, item_reader: Callable[[], T], delimiter: str, 
                        end_marker: str) -> List[T]:
    """
    Read a list of items separated by a delimiter until an end marker is found.
    
    Args:
        item_reader: Function that reads each item
        delimiter: String that separates items
        end_marker: String that marks the end of the list
        
    Returns:
        List of items read
    """
    result: List[T] = []
    
    token = self.try_read_next()
    if token is not None and token.value == end_marker:
        self.push_back(token)
        return result
        
    if token is not None:
        self.push_back(token)
        
    result.append(item_reader())
    
    while True:
        token = self.try_read_next()
        if token is None:
            raise ExpectedException(f"'{delimiter}' or '{end_marker}'", None)
            
        if token.value == end_marker:
            self.push_back(token)
            break
            
        if token.value != delimiter:
            raise ExpectedException(f"'{delimiter}' or '{end_marker}'", token)
            
        result.append(item_reader())
        
    return result


Tokenizer.read = read
Tokenizer.read_list = read_list
Tokenizer.read_delimited_list = read_delimited_list