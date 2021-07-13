# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import re

from more_itertools import peekable

from . import errors
from ._compat import unicode
from .tokens import (
    TOKENS,
    Dedent,
    End,
    Indent,
    LeftBrace,
    LeftRound,
    LeftSquare,
    NewLine,
    RightBrace,
    RightRound,
    RightSquare,
)
from .utils import lstripped

#: Flags to use in the Scanner class.
SCANNER_FLAGS = re.MULTILINE | re.UNICODE | re.VERBOSE


def _tokenize(input_string):
    position = len(lstripped(input_string)) + 1
    tokens, _ = _scanner.scan(input_string.strip())
    tokens = peekable(tokens)

    curr_indent = 0
    indent_stack = [0]
    newline_last = False
    inside_bracket = 0

    while tokens:
        indent_change = 0
        tok = next(tokens)
        tok.line = position

        # If inside brackets, no Indent/Dedent tokens are yielded.
        if tok.id in (LeftRound.id, LeftSquare.id, LeftBrace.id):
            inside_bracket += 1
        elif tok.id in (RightRound.id, RightSquare.id, RightBrace.id):
            inside_bracket -= 1

        # Determination of current indentation and indentation change
        # is necessary for correct generation of the Indent/Dedent tokens.
        if newline_last and not inside_bracket:
            indent = tok.value if tok.id == Indent.id else 0
            if indent != curr_indent:
                indent_change = indent - curr_indent
                curr_indent = indent

        # Here we determine the position of a token in the input string.
        if tok.id == NewLine.id:
            newline_last = True
            while tokens.peek().id == NewLine.id:
                tok.value = next(tokens).value
            position += tok.value
        else:
            newline_last = False

        # If indentation decreased we want to generate the needed dedent
        # tokens. These tokens are instantiated here as they cannot be
        # matched by regular expression.
        if indent_change < 0:
            while indent_stack[-1] > curr_indent:
                yield Dedent(indent_stack.pop(), line=position)
                yield NewLine(1, line=position)

        # If indentation increased we want to yield the indent token.
        if indent_change > 0:
            indent_stack.append(curr_indent)
            yield tok

        # We don't want to yield any other Indent tokens as our goal is
        # to represent the left/right braces with Indent/Dedent tokens.
        if tok.id != Indent.id and not (inside_bracket and tok.id == NewLine.id):
            yield tok

    while len(indent_stack) > 1:
        yield Dedent(indent_stack.pop(), line=position)


class tokenize(peekable):
    """Tokenizes an input string.

    :param input_string: String to be tokenized.
    :type input_string: str
    :return: List of pairs (token type, value).
    """

    def __init__(self, input_string):
        tokens = _tokenize(unicode(input_string))
        super(tokenize, self).__init__(tokens)

    def next(self):
        try:
            return self.__next__()
        except (StopIteration, RuntimeError):
            return End()

    def advance(self, allowed=None, skip=None):
        """Helper for iterating through tokens.

        :param allowed: Optional list of allowed tokens. Default is
            any token. If the found token is not allowed, the function
            raises syntax  error.
        :type allowed: :class:`Token` or iterable of tokens
        :param skip: If :obj:`True`, a sequence of given token types
            is skipped first. Default is :obj:`False`.
        :type skip: boolean
        """
        tok = self.next()
        if skip is not None:
            while tok.id == skip.id:
                tok = self.next()
        if allowed is None:
            return tok
        if not isinstance(allowed, (list, tuple)):
            allowed = [allowed]
        if all(tok.id != Token.id for Token in allowed):
            raise_error(allowed, tok)
        return tok

    def peek(self):
        try:
            return super(tokenize, self).peek()
        except (StopIteration, RuntimeError):
            return End()


def raise_error(expected, token):
    """Raises an error with some information about position etc.

    :param expected: List of expected tokens.
    :param token: Received token.
    :raises: :class:`errors.ParserError`
    """
    msg = "Unexpected {}".format(token.name)
    if token.line:
        msg += " on line {}".format(token.line)
    if expected and token.id != Indent.id:
        allowed_list = [Token.name for Token in expected if Token.re]
        if allowed_list:
            tok_msg = " or ".join(allowed_list)
            msg += ", expected {}".format(tok_msg)
    raise errors.ParserError(msg + ".")


def parse(input_string):
    """Parses given string according to NEON syntax.

    :param input_string: String to parse.
    :type input_string: string
    :return: Parsed string.
    :rtype: :class:`OrderedDict`
    """
    tokens = tokenize(input_string)
    return Indent().parse(tokens)


#: The Scanner is instantiated with a list of re's and associated
#: functions. It is used to scan a string, returning a list of parts
#: which match the given re's.
#:
#: See: http://stackoverflow.com/a/17214398/2874089
_scanner = re.Scanner(
    [TokenClass.getscan() for TokenClass in TOKENS if TokenClass.re is not None],
    flags=SCANNER_FLAGS,
)
