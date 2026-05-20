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
        token = self._peek()
        if token and token.value in ('int', 'char', 'boolean'):
            return self.tokenizer.try_read_next()
        return self._expect_identifier()

    def read_subroutine_dec(self, keyword: JackToken) -> SubroutineDecSyntax:
        """
        Parse a subroutine declaration.

        Grammar: ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        Note: keyword ('constructor', 'function', or 'method') is already consumed by the caller.
        """
        return_type = self.read_return_type()
        name = self._expect_identifier()
        open_paren = self._expect('(')
        parameters = self.read_parameter_list()
        close_paren = self._expect(')')
        body = self.read_subroutine_body()
        return SubroutineDecSyntax(keyword, return_type, name, open_paren, parameters, close_paren, body)

    def read_return_type(self) -> JackToken:
        """
        Parse a return type token.

        Grammar: 'void' | type
        Note: 'void' is a keyword; type is 'int', 'char', 'boolean', or a className identifier.
        """
        token = self._peek()
        if token and token.value == 'void':
            return self.tokenizer.try_read_next()
        return self.read_type()

    def read_parameter_list(self) -> ParameterListSyntax:
        """
        Parse a parameter list.

        Grammar: ((type varName) (',' type varName)*)?
        Note: The list may be empty. Stops before ')'.
        """
        parameters: List[Parameter] = []
        if self._peek() and self._peek().value == ')':
            return ParameterListSyntax(parameters)

        p_type = self.read_type()
        p_name = self._expect_identifier()
        parameters.append(Parameter(p_type, p_name))

        while self._peek() and self._peek().value == ',':
            self.tokenizer.try_read_next()
            p_type = self.read_type()
            p_name = self._expect_identifier()
            parameters.append(Parameter(p_type, p_name))

        return ParameterListSyntax(parameters)

    def read_subroutine_body(self) -> SubroutineBodySyntax:
        """
        Parse a subroutine body.

        Grammar: '{' varDec* statements '}'
        """
        open_brace = self._expect('{')

        var_decs: List[VarDecSyntax] = []
        while self._peek() and self._peek().value == 'var':
            var_keyword = self.tokenizer.try_read_next()
            var_decs.append(self.read_var_dec(var_keyword))

        statements = self.read_statements()
        close_brace = self._expect('}')

        return SubroutineBodySyntax(open_brace, var_decs, statements, close_brace)

    def read_var_dec(self, var_keyword: JackToken) -> VarDecSyntax:
        """
        Parse a local variable declaration.

        Grammar: 'var' type varName (',' varName)* ';'
        Note: var_keyword ('var') is already consumed by the caller.
        """
        type_token = self.read_type()
        names = [self._expect_identifier()]

        while self._peek() and self._peek().value == ',':
            self.tokenizer.try_read_next()
            names.append(self._expect_identifier())

        semicolon = self._expect(';')
        return VarDecSyntax(var_keyword, type_token, names, semicolon)

    def read_statements(self) -> StatementsSyntax:
        """
        Parse a sequence of statements.

        Grammar: statement*
        Note: Stops when '}' is encountered (or input ends). Does not consume the closing '}'.
        """
        statements: List[StatementSyntax] = []

        while True:
            token = self._peek()
            if token is None or token.value == '}':
                break

            if token.value == 'let':
                keyword = self.tokenizer.try_read_next()
                statements.append(self.read_let_statement(keyword))
            elif token.value == 'if':
                keyword = self.tokenizer.try_read_next()
                statements.append(self.read_if_statement(keyword))
            elif token.value == 'while':
                keyword = self.tokenizer.try_read_next()
                statements.append(self.read_while_statement(keyword))
            elif token.value == 'do':
                keyword = self.tokenizer.try_read_next()
                statements.append(self.read_do_statement(keyword))
            elif token.value == 'return':
                keyword = self.tokenizer.try_read_next()
                statements.append(self.read_return_statement(keyword))
            elif token.token_type == TokenType.IDENTIFIER:
                ident = self.tokenizer.try_read_next()
                next_token = self._peek()

                if next_token and next_token.value == '=':
                    self.tokenizer.push_back(ident)
                    dummy_let = JackToken(TokenType.KEYWORD, 'let', ident.line_number, ident.col_number)
                    statements.append(self.read_let_statement(dummy_let))
                elif next_token and next_token.value == '[':
                    self.tokenizer.push_back(ident)
                    dummy_let = JackToken(TokenType.KEYWORD, 'let', ident.line_number, ident.col_number)
                    statements.append(self.read_let_statement(dummy_let))
                elif next_token and (next_token.value == '(' or next_token.value == '.'):
                    self.tokenizer.push_back(ident)
                    dummy_do = JackToken(TokenType.KEYWORD, 'do', ident.line_number, ident.col_number)
                    statements.append(self.read_do_statement(dummy_do))
                else:
                    self.tokenizer.push_back(ident)
                    raise ExpectedException("statement keyword (let, if, while, do, return) or implicit start", token)
            else:
                raise ExpectedException("statement keyword (let, if, while, do, return)", token)

        return StatementsSyntax(statements)

    def read_let_statement(self, let_keyword: JackToken) -> LetStatementSyntax:
        """
        Parse a let statement.

        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        Note: let_keyword is already consumed by the caller.
        """
        var_name = self._expect_identifier()
        indexing = self.try_read_indexing()
        equals = self._expect('=')
        value = self.read_expression()
        semicolon = self._expect(';')
        return LetStatementSyntax(let_keyword, var_name, indexing, equals, value, semicolon)

    def read_if_statement(self, if_keyword: JackToken) -> IfStatementSyntax:
        """
        Parse an if statement.

        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        Note: if_keyword is already consumed by the caller.
        """
        open_paren = self._expect('(')
        condition = self.read_expression()
        close_paren = self._expect(')')
        open_true = self._expect('{')
        true_statements = self.read_statements()
        close_true = self._expect('}')
        else_clause = self.try_read_else_clause()
        return IfStatementSyntax(if_keyword, open_paren, condition, close_paren, open_true, true_statements, close_true, else_clause)

    def try_read_else_clause(self) -> Optional[ElseClause]:
        """
        Try to parse an optional else clause.

        Grammar: ('else' '{' statements '}')?
        Returns None if the next token is not 'else'.
        """
        if self._peek() and self._peek().value == 'else':
            else_keyword = self.tokenizer.try_read_next()
            open_brace = self._expect('{')
            statements = self.read_statements()
            close_brace = self._expect('}')
            return ElseClause(else_keyword, open_brace, statements, close_brace)
        return None

    def read_while_statement(self, while_keyword: JackToken) -> WhileStatementSyntax:
        """
        Parse a while statement.

        Grammar: 'while' '(' expression ')' '{' statements '}'
        Note: while_keyword is already consumed by the caller.
        """
        open_paren = self._expect('(')
        condition = self.read_expression()
        close_paren = self._expect(')')
        open_brace = self._expect('{')
        statements = self.read_statements()
        close_brace = self._expect('}')
        return WhileStatementSyntax(while_keyword, open_paren, condition, close_paren, open_brace, statements, close_brace)

    def read_do_statement(self, do_keyword: JackToken) -> DoStatementSyntax:
        """
        Parse a do statement.

        Grammar: 'do' subroutineCall ';'
        Note: do_keyword is already consumed by the caller.
        """
        subroutine_call = self.read_subroutine_call()
        semicolon = self._expect(';')
        return DoStatementSyntax(do_keyword, subroutine_call, semicolon)

    def read_return_statement(self, return_keyword: JackToken) -> ReturnStatementSyntax:
        """
        Parse a return statement.

        Grammar: 'return' expression? ';'
        Note: return_keyword is already consumed by the caller.
        """
        expression = None
        if not (self._peek() and self._peek().value == ';'):
            expression = self.read_expression()
        semicolon = self._expect(';')
        return ReturnStatementSyntax(return_keyword, expression, semicolon)

    def read_expression(self) -> ExpressionSyntax:
        """
        Parse an expression.

        Grammar: term (op term)*
        Operators: + - * / & | < > =
        Note: Jack has NO operator precedence - evaluate strictly left-to-right.
        """
        first_term = self.read_term()
        operations: List[Tuple[JackToken, TermSyntax]] = []

        while self._peek() and self._peek().value in OPERATORS:
            op = self.tokenizer.try_read_next()
            term = self.read_term()
            operations.append((op, term))

        return ExpressionSyntax(first_term, operations)

    def read_term(self) -> TermSyntax:
        """
        Parse a term.

        Grammar: integerConstant | stringConstant | keywordConstant |
                 varName | varName '[' expression ']' |
                 subroutineCall | '(' expression ')' | unaryOp term
        Keyword constants: true, false, null, this
        Unary operators: - ~
        """
        token = self._peek()
        
        if token is None:
            raise ExpectedException("term", None)

        if token.token_type == TokenType.INTEGER_CONSTANT:
            t = self.tokenizer.try_read_next()
            return IntegerConstantTerm(t)

        if token.token_type == TokenType.STRING_CONSTANT:
            t = self.tokenizer.try_read_next()
            return StringConstantTerm(t)

        if token.token_type == TokenType.KEYWORD:
            if token.value in KEYWORD_CONSTANTS:
                if token.value == 'this':
                    self.tokenizer.try_read_next()
                    next_token = self._peek()
                    
                    if next_token and (next_token.value == '.' or next_token.value == '('):
                        self.tokenizer.push_back(token)
                    else:
                        return KeywordConstantTerm(token)
                else:
                    t = self.tokenizer.try_read_next()
                    return KeywordConstantTerm(t)

        if token.value in UNARY_OPS:
            op = self.tokenizer.try_read_next()
            term = self.read_term()
            return UnaryOpTerm(op, term)

        if token.value == '(':
            open_paren = self.tokenizer.try_read_next()
            expr = self.read_expression()
            close_paren = self._expect(')')
            return ParenthesizedTerm(open_paren, expr, close_paren)

        if token.token_type == TokenType.IDENTIFIER or (token.token_type == TokenType.KEYWORD and token.value == 'this'):
            name_token = self.tokenizer.try_read_next()
            next_token = self._peek()

            if next_token and next_token.value == '[':
                indexing = self.try_read_indexing()
                return IndexedVarTerm(name_token, indexing)
            elif next_token and (next_token.value == '(' or next_token.value == '.'):
                self.tokenizer.push_back(name_token)
                call = self.read_subroutine_call()
                return SubroutineCallTerm(call)
            else:
                return VarNameTerm(name_token)

        raise ExpectedException("term", token)

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
