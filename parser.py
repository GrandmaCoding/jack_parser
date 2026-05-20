from typing import Optional, List, Callable, Any, cast, Tuple

from .jack_token import JackToken
from .tokenizer import Tokenizer
from .token_type import TokenType
from .exceptions import ExpectedException
from . import tokenizer_extensions

from .jack_syntax import (
    ClassSyntax, ClassVarDecSyntax, Parameter, ParameterListSyntax,
    SubroutineDecSyntax, SubroutineBodySyntax, VarDecSyntax, StatementsSyntax,
    StatementSyntax, LetStatementSyntax, Indexing, IfStatementSyntax, ElseClause,
    WhileStatementSyntax, DoStatementSyntax, ReturnStatementSyntax, ExpressionSyntax,
    TermSyntax, IntegerConstantTerm, StringConstantTerm, KeywordConstantTerm,
    VarNameTerm, IndexedVarTerm, ParenthesizedTerm, UnaryOpTerm, SubroutineCallTerm,
    SubroutineCall, ExpressionListSyntax
)

OPERATORS = set('+-*/&|<>=')
UNARY_OPS = set('-~')
KEYWORD_CONSTANTS = {'true', 'false', 'null', 'this'}


class Parser:
    """Parser for the Jack language that builds an abstract syntax tree."""

    def __init__(self, tokenizer: Tokenizer):
        """
        Initialize the parser with a tokenizer.

        Args:
            tokenizer: The tokenizer to use for reading tokens
        """
        self.tokenizer = tokenizer

    def _expect(self, value: str) -> JackToken:
        """Read a token and expect it to have the given value."""
        token = self.tokenizer.try_read_next()
        if token is None or token.value != value:
            raise ExpectedException(f"'{value}'", token)
        return token

    def _expect_type(self, token_type: TokenType, description: str) -> JackToken:
        """Read a token and expect it to have the given type."""
        token = self.tokenizer.try_read_next()
        if token is None or token.token_type != token_type:
            raise ExpectedException(description, token)
        return token

    def _expect_identifier(self) -> JackToken:
        """Read a token and expect an identifier."""
        return self._expect_type(TokenType.IDENTIFIER, "identifier")

    def read_class(self) -> ClassSyntax:
        """
        Parse a Jack class definition.

        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        class_keyword = self._expect('class')
        name = self._expect_identifier()
        open_brace = self._expect('{')

        var_decs: List[ClassVarDecSyntax] = []
        while True:
            token = self._peek()
            if token and token.value in ('static', 'field'):
                keyword = self.tokenizer.try_read_next()
                var_decs.append(self.read_class_var_dec(keyword))
            else:
                break

        subroutines: List[SubroutineDecSyntax] = []
        while True:
            token = self._peek()
            if token and token.value in ('constructor', 'function', 'method'):
                keyword = self.tokenizer.try_read_next()
                subroutines.append(self.read_subroutine_dec(keyword))
            else:
                break

        close_brace = self._expect('}')
        return ClassSyntax(class_keyword, name, open_brace, var_decs, subroutines, close_brace)

    def read_class_var_dec(self, kind_keyword: JackToken) -> ClassVarDecSyntax:
        """
        Parse a class variable declaration.

        Grammar: ('static'|'field') type varName (',' varName)* ';'
        Note: kind_keyword ('static' or 'field') is already consumed by the caller.
        """
        type_token = self.read_type()
        names = [self._expect_identifier()]

        while self._peek() and self._peek().value == ',':
            self.tokenizer.try_read_next()
            names.append(self._expect_identifier())

        semicolon = self._expect(';')
        return ClassVarDecSyntax(kind_keyword, type_token, names, semicolon)

    def read_type(self) -> JackToken:
        """
        Parse a type token.

        Grammar: 'int' | 'char' | 'boolean' | className
        Note: className is an identifier.
        """
        raise NotImplementedError()

    def read_subroutine_dec(self, keyword: JackToken) -> SubroutineDecSyntax:
        """
        Parse a subroutine declaration.

        Grammar: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        Note: keyword ('constructor', 'function', or 'method') is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_return_type(self) -> JackToken:
        """
        Parse a return type token.

        Grammar: 'void' | type
        Note: 'void' is a keyword; type is 'int', 'char', 'boolean', or a className identifier.
        """
        raise NotImplementedError()

    def read_parameter_list(self) -> ParameterListSyntax:
        """
        Parse a parameter list.

        Grammar: ((type varName) (',' type varName)*)?
        Note: The list may be empty. Stops before ')'.
        """
        raise NotImplementedError()

    def read_subroutine_body(self) -> SubroutineBodySyntax:
        """
        Parse a subroutine body.

        Grammar: '{' varDec* statements '}'
        """
        raise NotImplementedError()

    def read_var_dec(self, var_keyword: JackToken) -> VarDecSyntax:
        """
        Parse a local variable declaration.

        Grammar: 'var' type varName (',' varName)* ';'
        Note: var_keyword ('var') is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_statements(self) -> StatementsSyntax:
        """
        Parse a sequence of statements.

        Grammar: statement*
        Note: Stops when '}' is encountered (or input ends). Does not consume the closing '}'.
        """
        raise NotImplementedError()

    def read_let_statement(self, let_keyword: JackToken) -> LetStatementSyntax:
        """
        Parse a let statement.

        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        Note: let_keyword is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_if_statement(self, if_keyword: JackToken) -> IfStatementSyntax:
        """
        Parse an if statement.

        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        Note: if_keyword is already consumed by the caller.
        """
        raise NotImplementedError()

    def try_read_else_clause(self) -> Optional[ElseClause]:
        """
        Try to parse an optional else clause.

        Grammar: ('else' '{' statements '}')?
        Returns None if the next token is not 'else'.
        """
        raise NotImplementedError()

    def read_while_statement(self, while_keyword: JackToken) -> WhileStatementSyntax:
        """
        Parse a while statement.

        Grammar: 'while' '(' expression ')' '{' statements '}'
        Note: while_keyword is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_do_statement(self, do_keyword: JackToken) -> DoStatementSyntax:
        """
        Parse a do statement.

        Grammar: 'do' subroutineCall ';'
        Note: do_keyword is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_return_statement(self, return_keyword: JackToken) -> ReturnStatementSyntax:
        """
        Parse a return statement.

        Grammar: 'return' expression? ';'
        Note: return_keyword is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_expression(self) -> ExpressionSyntax:
        """
        Parse an expression.

        Grammar: term (op term)*
        Operators: + - * / & | < > =
        Note: Jack has NO operator precedence - evaluate strictly left-to-right.
        """
        raise NotImplementedError()

    def read_term(self) -> TermSyntax:
        """
        Parse a term.

        Grammar: integerConstant | stringConstant | keywordConstant |
                 varName | varName '[' expression ']' |
                 subroutineCall | '(' expression ')' | unaryOp term
        Keyword constants: true, false, null, this
        Unary operators: - ~
        """
        raise NotImplementedError()

    def read_subroutine_call(self) -> SubroutineCall:
        """
        Parse a subroutine call.

        Grammar: subroutineName '(' expressionList ')' |
                 (className | varName) '.' subroutineName '(' expressionList ')'
        """
        raise NotImplementedError()

    def try_read_indexing(self) -> Optional[Indexing]:
        """
        Try to parse optional array indexing.

        Grammar: ('[' expression ']')?
        Returns None if the next token is not '['.
        Note: The preceding identifier (varName) is already consumed by the caller.
        """
        raise NotImplementedError()

    def read_expression_list(self) -> ExpressionListSyntax:
        """
        Parse a comma-separated list of expressions.

        Grammar: (expression (',' expression)*)?
        Note: The list may be empty. Stops before ')' without consuming it.
        """
        raise NotImplementedError()
