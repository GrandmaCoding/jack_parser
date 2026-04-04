from typing import Any, List, Type
import html
from .token_type import TokenType
from .jack_token import JackToken
from .syntax_writer import SyntaxWriter
from .jack_syntax import (
    ClassSyntax, ClassVarDecSyntax, SubroutineDecSyntax, ParameterListSyntax,
    Parameter, SubroutineBodySyntax, VarDecSyntax, StatementsSyntax, StatementSyntax,
    LetStatementSyntax, IfStatementSyntax, WhileStatementSyntax, DoStatementSyntax,
    ReturnStatementSyntax, ExpressionSyntax, TermSyntax, IntegerConstantTerm,
    StringConstantTerm, KeywordConstantTerm, VarNameTerm, IndexedVarTerm,
    ParenthesizedTerm, UnaryOpTerm, SubroutineCallTerm, SubroutineCall,
    ExpressionListSyntax, ElseClause, Indexing
)


class XmlSyntaxWriter(SyntaxWriter):
    """
    Syntax writer that produces XML output.
    
    Used for debugging and visualizing the parse tree.
    """
    
    def __init__(self):
        """Initialize the writer."""
        super().__init__()
        self.indent_level = 0
    
    def _write_token(self, token: JackToken) -> None:
        """Write a token to XML."""
        token_type_name = token.token_type.name.lower() if hasattr(token, 'token_type') else "token"
        if hasattr(token, 'token_type'):
            if token.token_type == TokenType.KEYWORD:
                element_name = "keyword"
            elif token.token_type == TokenType.SYMBOL:
                element_name = "symbol"
            elif token.token_type == TokenType.IDENTIFIER:
                element_name = "identifier"
            elif token.token_type == TokenType.INTEGER_CONSTANT:
                element_name = "integerConstant"
            elif token.token_type == TokenType.STRING_CONSTANT:
                element_name = "stringConstant"
            else:
                element_name = f"unknown_{token_type_name}"
        else:
            element_name = "token"
        
        value = self._escape_xml(token.value)
        self._write_line(f"<{element_name}> {value} </{element_name}>")
    
    def open_container_tag(self, type_: Type) -> None:
        """
        Open a container tag.
        
        Args:
            type_: The type of the container
        """
        tag_name = self.get_tag_name(type_)
        self._write_line(f"<{tag_name}>")
        self.indent_level += 1
    
    def close_container_tag(self, type_: Type) -> None:
        """
        Close a container tag.
        
        Args:
            type_: The type of the container
        """
        self.indent_level -= 1
        tag_name = self.get_tag_name(type_)
        self._write_line(f"</{tag_name}>")

    def _write_element_start(self, element_name: str) -> None:
        """Write the start tag of an XML element."""
        self._write_line(f"<{element_name}>")
    
    def _write_element_end(self, element_name: str) -> None:
        """Write the end tag of an XML element."""
        self._write_line(f"</{element_name}>")
    
    def _write_line(self, line: str) -> None:
        """Write a line to the result with proper indentation."""
        indent = "  " * self.indent_level
        self.result.append(f"{indent}{line}")
    
    def _write_raw_token(self, value: str, tag: str) -> None:
        """Write a raw token (not from the syntax tree) to XML."""
        escaped_value = self._escape_xml(value)
        self._write_line(f"<{tag}> {escaped_value} </{tag}>")
    
    def _escape_xml(self, text: str) -> str:
        """Escape special characters in XML."""
        # Custom handling for specific symbols
        if text == "<":
            return "&lt;"
        elif text == ">":
            return "&gt;"
        elif text == "&":
            return "&amp;"
        else:
            return html.escape(text)
            
    def write(self, syntax: Any) -> None:
        """
        Write a syntax element to the result based on its type.
        
        Args:
            syntax: The syntax element to write
        """
        if isinstance(syntax, ClassSyntax):
            self.write_class(syntax)
        elif isinstance(syntax, ClassVarDecSyntax):
            self.write_class_var_dec(syntax)
        elif isinstance(syntax, SubroutineDecSyntax):
            self.write_subroutine_dec(syntax)
        elif isinstance(syntax, ParameterListSyntax):
            self.write_parameter_list(syntax)
        elif isinstance(syntax, SubroutineBodySyntax):
            self.write_subroutine_body(syntax)
        elif isinstance(syntax, VarDecSyntax):
            self.write_var_dec(syntax)
        elif isinstance(syntax, StatementsSyntax):
            self.write_statements(syntax)
        elif isinstance(syntax, LetStatementSyntax):
            self.write_let_statement(syntax)
        elif isinstance(syntax, IfStatementSyntax):
            self.write_if_statement(syntax)
        elif isinstance(syntax, WhileStatementSyntax):
            self.write_while_statement(syntax)
        elif isinstance(syntax, DoStatementSyntax):
            self.write_do_statement(syntax)
        elif isinstance(syntax, ReturnStatementSyntax):
            self.write_return_statement(syntax)
        elif isinstance(syntax, ExpressionSyntax):
            self.write_expression(syntax)
        elif isinstance(syntax, IntegerConstantTerm):
            self.write_integer_constant_term(syntax)
        elif isinstance(syntax, StringConstantTerm):
            self.write_string_constant_term(syntax)
        elif isinstance(syntax, KeywordConstantTerm):
            self.write_keyword_constant_term(syntax)
        elif isinstance(syntax, VarNameTerm):
            self.write_var_name_term(syntax)
        elif isinstance(syntax, IndexedVarTerm):
            self.write_indexed_var_term(syntax)
        elif isinstance(syntax, ParenthesizedTerm):
            self.write_parenthesized_term(syntax)
        elif isinstance(syntax, UnaryOpTerm):
            self.write_unary_op_term(syntax)
        elif isinstance(syntax, SubroutineCallTerm):
            self.write_subroutine_call_term(syntax)
        elif isinstance(syntax, SubroutineCall):
            self.write_subroutine_call(syntax)
        elif isinstance(syntax, ExpressionListSyntax):
            self.write_expression_list(syntax)
        elif isinstance(syntax, JackToken):
            self._write_token(syntax)
        else:
            raise ValueError(f"Unknown syntax type: {type(syntax)}")
    
    def write_class(self, syntax: ClassSyntax) -> None:
        """Write a class definition to XML."""
        self._write_element_start("class")
        self.indent_level += 1
        
        self.write(syntax.class_keyword)
        self.write(syntax.name)
        self.write(syntax.open_brace)
        
        for var_dec in syntax.var_decs:
            self.write(var_dec)
            
        for subroutine in syntax.subroutines:
            self.write(subroutine)
            
        self.write(syntax.close_brace)
        
        self.indent_level -= 1
        self._write_element_end("class")
    
    def write_class_var_dec(self, syntax: ClassVarDecSyntax) -> None:
        """Write a class variable declaration to XML."""
        self._write_element_start("classVarDec")
        self.indent_level += 1
        
        self.write(syntax.kind_keyword)
        self.write(syntax.type_token)
        
        for i, name in enumerate(syntax.names):
            self.write(name)
            if i < len(syntax.names) - 1:
                self._write_raw_token(",", "symbol")
                
        self.write(syntax.semicolon)
        
        self.indent_level -= 1
        self._write_element_end("classVarDec")
    
    def write_subroutine_dec(self, syntax: SubroutineDecSyntax) -> None:
        """Write a subroutine declaration to XML."""
        self._write_element_start("subroutineDec")
        self.indent_level += 1
        
        self.write(syntax.keyword)
        self.write(syntax.return_type)
        self.write(syntax.name)
        self.write(syntax.open_paren)
        self.write(syntax.parameters)
        self.write(syntax.close_paren)
        self.write(syntax.body)
        
        self.indent_level -= 1
        self._write_element_end("subroutineDec")
    
    def write_parameter_list(self, syntax: ParameterListSyntax) -> None:
        """Write a parameter list to XML."""
        self._write_element_start("parameterList")
        self.indent_level += 1
        
        for i, param in enumerate(syntax.parameters):
            self.write(param.type_token)
            self.write(param.name)
            if i < len(syntax.parameters) - 1:
                self._write_raw_token(",", "symbol")
                
        self.indent_level -= 1
        self._write_element_end("parameterList")
    
    def write_subroutine_body(self, syntax: SubroutineBodySyntax) -> None:
        """Write a subroutine body to XML."""
        self._write_element_start("subroutineBody")
        self.indent_level += 1
        
        self.write(syntax.open_brace)
        
        for var_dec in syntax.var_decs:
            self.write(var_dec)
            
        self.write(syntax.statements)
        self.write(syntax.close_brace)
        
        self.indent_level -= 1
        self._write_element_end("subroutineBody")
    
    def write_var_dec(self, syntax: VarDecSyntax) -> None:
        """Write a variable declaration to XML."""
        self._write_element_start("varDec")
        self.indent_level += 1
        
        self.write(syntax.var_keyword)
        self.write(syntax.type_token)
        
        for i, name in enumerate(syntax.names):
            self.write(name)
            if i < len(syntax.names) - 1:
                self._write_raw_token(",", "symbol")
                
        self.write(syntax.semicolon)
        
        self.indent_level -= 1
        self._write_element_end("varDec")
    
    def write_statements(self, syntax: StatementsSyntax) -> None:
        """Write statements to XML."""
        self._write_element_start("statements")
        self.indent_level += 1
        
        for statement in syntax.statements:
            self.write(statement)
            
        self.indent_level -= 1
        self._write_element_end("statements")
    
    def write_let_statement(self, syntax: LetStatementSyntax) -> None:
        """Write a let statement to XML."""
        self._write_element_start("letStatement")
        self.indent_level += 1
        
        self.write(syntax.let_keyword)
        self.write(syntax.var_name)
        
        if syntax.indexing:
            self.write(syntax.indexing.open_bracket)
            self.write(syntax.indexing.index)
            self.write(syntax.indexing.close_bracket)
            
        self.write(syntax.equals)
        self.write(syntax.value)
        self.write(syntax.semicolon)
        
        self.indent_level -= 1
        self._write_element_end("letStatement")
    
    def write_if_statement(self, syntax: IfStatementSyntax) -> None:
        """Write an if statement to XML."""
        self._write_element_start("ifStatement")
        self.indent_level += 1
        
        self.write(syntax.if_keyword)
        self.write(syntax.open_paren)
        self.write(syntax.condition)
        self.write(syntax.close_paren)
        self.write(syntax.open_true)
        self.write(syntax.true_statements)
        self.write(syntax.close_true)
        
        if syntax.else_clause:
            self.write(syntax.else_clause.else_keyword)
            self.write(syntax.else_clause.open_brace)
            self.write(syntax.else_clause.statements)
            self.write(syntax.else_clause.close_brace)
            
        self.indent_level -= 1
        self._write_element_end("ifStatement")
    
    def write_while_statement(self, syntax: WhileStatementSyntax) -> None:
        """Write a while statement to XML."""
        self._write_element_start("whileStatement")
        self.indent_level += 1
        
        self.write(syntax.while_keyword)
        self.write(syntax.open_paren)
        self.write(syntax.condition)
        self.write(syntax.close_paren)
        self.write(syntax.open_brace)
        self.write(syntax.statements)
        self.write(syntax.close_brace)
        
        self.indent_level -= 1
        self._write_element_end("whileStatement")
    
    def write_do_statement(self, syntax: DoStatementSyntax) -> None:
        """Write a do statement to XML."""
        self._write_element_start("doStatement")
        self.indent_level += 1
        
        self.write(syntax.do_keyword)
        self.write(syntax.subroutine_call)
        self.write(syntax.semicolon)
        
        self.indent_level -= 1
        self._write_element_end("doStatement")
    
    def write_return_statement(self, syntax: ReturnStatementSyntax) -> None:
        """Write a return statement to XML."""
        self._write_element_start("returnStatement")
        self.indent_level += 1
        
        self.write(syntax.return_keyword)
        
        if syntax.expression:
            self.write(syntax.expression)
            
        self.write(syntax.semicolon)
        
        self.indent_level -= 1
        self._write_element_end("returnStatement")
    
    def write_expression(self, syntax: ExpressionSyntax) -> None:
        """Write an expression to XML."""
        self._write_element_start("expression")
        self.indent_level += 1
        
        self.write(syntax.first_term)
        
        for operator, term in syntax.operations:
            self.write(operator)
            self.write(term)
            
        self.indent_level -= 1
        self._write_element_end("expression")
    
    def write_integer_constant_term(self, syntax: IntegerConstantTerm) -> None:
        """Write an integer constant term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.token)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_string_constant_term(self, syntax: StringConstantTerm) -> None:
        """Write a string constant term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.token)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_keyword_constant_term(self, syntax: KeywordConstantTerm) -> None:
        """Write a keyword constant term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.token)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_var_name_term(self, syntax: VarNameTerm) -> None:
        """Write a variable name term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.name)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_indexed_var_term(self, syntax: IndexedVarTerm) -> None:
        """Write an indexed variable term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.name)
        self.write(syntax.indexing.open_bracket)
        self.write(syntax.indexing.index)
        self.write(syntax.indexing.close_bracket)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_parenthesized_term(self, syntax: ParenthesizedTerm) -> None:
        """Write a parenthesized term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.open_paren)
        self.write(syntax.expression)
        self.write(syntax.close_paren)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_unary_op_term(self, syntax: UnaryOpTerm) -> None:
        """Write a unary operation term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.operator)
        self.write(syntax.term)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_subroutine_call_term(self, syntax: SubroutineCallTerm) -> None:
        """Write a subroutine call term to XML."""
        self._write_element_start("term")
        self.indent_level += 1
        
        self.write(syntax.call)
        
        self.indent_level -= 1
        self._write_element_end("term")
    
    def write_subroutine_call(self, syntax: SubroutineCall) -> None:
        """Write a subroutine call to XML."""
        if syntax.obj_name:
            self.write(syntax.obj_name)
            self.write(syntax.dot)
            
        self.write(syntax.subroutine_name)
        self.write(syntax.open_paren)
        self.write(syntax.arguments)
        self.write(syntax.close_paren)
    
    def write_expression_list(self, syntax: ExpressionListSyntax) -> None:
        """Write an expression list to XML."""
        self._write_element_start("expressionList")
        self.indent_level += 1
        
        for i, expr in enumerate(syntax.expressions):
            self.write(expr)
            if i < len(syntax.expressions) - 1:
                self._write_raw_token(",", "symbol")
                
        self.indent_level -= 1
        self._write_element_end("expressionList") 