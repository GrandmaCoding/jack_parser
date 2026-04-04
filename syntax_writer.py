from typing import List, Any, Optional, Type, get_type_hints
from abc import ABC, abstractmethod
import inspect
from collections.abc import Iterable

from .jack_token import JackToken
from .jack_syntax import (
    ClassSyntax, ClassVarDecSyntax, SubroutineDecSyntax, ParameterListSyntax,
    Parameter, SubroutineBodySyntax, VarDecSyntax, StatementsSyntax, StatementSyntax,
    LetStatementSyntax, IfStatementSyntax, WhileStatementSyntax, DoStatementSyntax,
    ReturnStatementSyntax, ExpressionSyntax, TermSyntax, IntegerConstantTerm,
    StringConstantTerm, KeywordConstantTerm, VarNameTerm, IndexedVarTerm,
    ParenthesizedTerm, UnaryOpTerm, SubroutineCallTerm, SubroutineCall,
    ExpressionListSyntax
)


class SyntaxWriter(ABC):
    """
    Abstract base class for syntax writers.
    
    Syntax writers are responsible for serializing the syntax tree
    into a specific format (e.g., XML, VM code).
    """
    
    def __init__(self):
        """Initialize the writer."""
        self.result: List[str] = []
    
    def get_result(self) -> List[str]:
        """Get the result of the writing process."""
        return self.result
    
    def append(self, text: str) -> None:
        """
        Append text to the result.
        
        Args:
            text: The text to append
        """
        if len(self.result) == 0:
            self.result.append(text)
        else:
            self.result[-1] += text
    
    def get_tag_name(self, type_: Type) -> str:
        """
        Get the tag name for a type.
        
        Args:
            type_: The type to get the tag name for
            
        Returns:
            The tag name
        """
        if issubclass(type_, TermSyntax):
            return "term"
        
        type_name = type_.__name__
        if type_name.endswith('Syntax'):
            base_name = type_name[:-6]
            return base_name[0].lower() + base_name[1:]
        else:
            return type_name[0].lower() + type_name[1:]

    def write(self, syntax: Any) -> None:
        """
        Write a syntax element to the result.
        
        Args:
            syntax: The syntax element to write
        """
        if syntax is None:
            return

        if isinstance(syntax, JackToken):
            self._write_token(syntax)
            return

        current_type = type(syntax)
        
        is_container_node = current_type.__name__.endswith('Syntax') or issubclass(current_type, TermSyntax)
        
        if is_container_node:
            self.open_container_tag(current_type) # Uses the updated get_tag_name

        if hasattr(syntax, '__dict__'):
            for name, value in vars(syntax).items():
                if name.startswith('_'):
                    continue
                
                if isinstance(value, list):
                    self._write_list(value, name.startswith('delimited_'))
                else:
                    self.write(value)
        elif isinstance(syntax, tuple) and hasattr(syntax, '_fields'): 
            for field_name in syntax._fields:
                value = getattr(syntax, field_name)
                if isinstance(value, list):
                    self._write_list(value, field_name.startswith('delimited_'))
                else:
                    self.write(value)

        
        if is_container_node:
            self.close_container_tag(current_type)
    
    def _write_list(self, items: List[Any], delimit: bool) -> None:
        """
        Write a list of items, optionally separated by commas.
        
        Args:
            items: The list of items to write
            delimit: Whether to separate items with commas
        """
        for i, item in enumerate(items):
            self.write(item)
            if delimit and i < len(items) - 1:
                self._write_token(',')
    
    @abstractmethod
    def _write_token(self, token: Any) -> None: 
        """
        Write a token. This method should be implemented by subclasses.
        
        Args:
            token: The token to write
        """
        pass
        
    @abstractmethod
    def open_container_tag(self, type_: Type) -> None:
        """
        Open a container tag.
        
        Args:
            type_: The type of the container
        """
        pass
        
    @abstractmethod
    def close_container_tag(self, type_: Type) -> None:
        """
        Close a container tag.
        
        Args:
            type_: The type of the container
        """
        pass
        

    def write_class(self, syntax: ClassSyntax) -> None:
        """Write a class syntax element."""
        self.write(syntax)
        
    def write_class_var_dec(self, syntax: ClassVarDecSyntax) -> None:
        """Write a class variable declaration syntax element."""
        self.write(syntax)
        
    def write_subroutine_dec(self, syntax: SubroutineDecSyntax) -> None:
        """Write a subroutine declaration syntax element."""
        self.write(syntax)
        
    def write_parameter_list(self, syntax: ParameterListSyntax) -> None:
        """Write a parameter list syntax element."""
        self.write(syntax)
        
    def write_subroutine_body(self, syntax: SubroutineBodySyntax) -> None:
        """Write a subroutine body syntax element."""
        self.write(syntax)
        
    def write_var_dec(self, syntax: VarDecSyntax) -> None:
        """Write a variable declaration syntax element."""
        self.write(syntax)
        
    def write_statements(self, syntax: StatementsSyntax) -> None:
        """Write a statements syntax element."""
        self.write(syntax)
        
    def write_statement(self, syntax: StatementSyntax) -> None:
        """Write a statement syntax element."""
        self.write(syntax)
        
    def write_let_statement(self, syntax: LetStatementSyntax) -> None:
        """Write a let statement syntax element."""
        self.write(syntax)
        
    def write_if_statement(self, syntax: IfStatementSyntax) -> None:
        """Write an if statement syntax element."""
        self.write(syntax)
        
    def write_while_statement(self, syntax: WhileStatementSyntax) -> None:
        """Write a while statement syntax element."""
        self.write(syntax)
        
    def write_do_statement(self, syntax: DoStatementSyntax) -> None:
        """Write a do statement syntax element."""
        self.write(syntax)
        
    def write_return_statement(self, syntax: ReturnStatementSyntax) -> None:
        """Write a return statement syntax element."""
        self.write(syntax)
        
    def write_expression(self, syntax: ExpressionSyntax) -> None:
        """Write an expression syntax element."""
        self.write(syntax)
        
    def write_term(self, syntax: TermSyntax) -> None:
        """Write a term syntax element."""
        self.write(syntax)
        
    def write_subroutine_call(self, syntax: SubroutineCall) -> None:
        """Write a subroutine call syntax element."""
        self.write(syntax)
        
    def write_expression_list(self, syntax: ExpressionListSyntax) -> None:
        """Write an expression list syntax element."""
        self.write(syntax) 