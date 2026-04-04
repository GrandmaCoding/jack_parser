from typing import Type, Any
from .syntax_writer import SyntaxWriter
from .jack_token import JackToken
from .jack_syntax import TermSyntax, ExpressionSyntax, ExpressionListSyntax, ParameterListSyntax, Parameter, ClassVarDecSyntax, VarDecSyntax
from .token_type import TokenType

class CompactSyntaxWriter(SyntaxWriter):
    def __init__(self):
        super().__init__()
        self.need_space = False
        
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
            self.open_container_tag(current_type)

        if isinstance(syntax, ExpressionSyntax):
             self.write(syntax.first_term)
            
             for op_token, term_syntax in syntax.operations:
                 self._write_token(op_token)
                 self.write(term_syntax)

        elif issubclass(current_type, TermSyntax):
           
            if hasattr(syntax, 'token'):
                self.write(syntax.token)
            elif hasattr(syntax, 'name') and not hasattr(syntax, 'call'): 
                self.write(syntax.name)
                if hasattr(syntax, 'indexing') and syntax.indexing is not None:
                    self._write_token(syntax.indexing.open_bracket) 
                    self.write(syntax.indexing.index)       
                    self._write_token(syntax.indexing.close_bracket)
            elif hasattr(syntax, 'operator') and hasattr(syntax, 'term'): 
                self._write_token(syntax.operator)
                self.write(syntax.term)
            elif hasattr(syntax, 'expression') and hasattr(syntax, 'open_paren'): 
                self._write_token(syntax.open_paren)
                self.write(syntax.expression)
                self._write_token(syntax.close_paren)
            elif hasattr(syntax, 'call'):
                self.write(syntax.call)
            else:
        
                for field_name in syntax.__dataclass_fields__:
                    if field_name.startswith('_'): continue
                    value = getattr(syntax, field_name)
                    if value is not None:
                        self.write(value)
    
        elif isinstance(syntax, ExpressionListSyntax):
            for i, expr in enumerate(syntax.expressions):
                self.write(expr)
                if i < len(syntax.expressions) - 1:
                    self._write_token(',')

        elif isinstance(syntax, ParameterListSyntax):
            for i, param in enumerate(syntax.parameters):
                self.write(param.type_token)
                self.write(param.name)
                if i < len(syntax.parameters) - 1:
                    self._write_token(',')
        elif isinstance(syntax, ClassVarDecSyntax):
            self.write(syntax.kind_keyword)
            self.write(syntax.type_token)
            for i, name_token in enumerate(syntax.names):
                self.write(name_token)
                if i < len(syntax.names) - 1:
                    self._write_token(',')
            self.write(syntax.semicolon)
        elif isinstance(syntax, VarDecSyntax):
            self.write(syntax.var_keyword)
            self.write(syntax.type_token)
            for i, name_token in enumerate(syntax.names):
                self.write(name_token)
                if i < len(syntax.names) - 1:
                    self._write_token(',')
            self.write(syntax.semicolon)
        elif hasattr(syntax, '__dict__'):
            for name, value in vars(syntax).items():
                if name.startswith('_'):
                    continue
                if value is not None:
                    if isinstance(value, list):
                    
                        self._write_list(value, name.startswith('delimited_'))
                    else:
                        self.write(value)
        
        if is_container_node:

             self.close_container_tag(current_type)

    def _write_token(self, token: Any) -> None:
        """Writes a token, managing spaces based on the simpler C# logic."""
        value_to_write = str(token.value if isinstance(token, JackToken) else token)

        if self.need_space:
             self.append(" ")

        self.append(value_to_write)

        self.need_space = True

    def open_container_tag(self, type_: Type) -> None:
        tag_name = self.get_tag_name(type_)
        if self.need_space and tag_name:
             self.append(" ")
        self.append(f"{tag_name}[")
        self.need_space = False 

    def close_container_tag(self, type_: Type) -> None:
        self.append("]")
        self.need_space = True