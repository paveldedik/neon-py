# -*- coding: utf-8 -*-


import re
from collections import OrderedDict

from . import errors
from .utils import lstripped, peekable
from .tokens import (
    TOKENS, NewLine, Indent, Dedent, Colon, End,
    LeftBrace, LeftSquare, LeftRound, RightBrace, RightSquare, RightRound,
)


#: Flags to use for the Scanner class.
SCANNER_FLAGS = re.MULTILINE | re.UNICODE | re.VERBOSE


def _tokenize(input_string):
    position = len(lstripped(input_string)) + 1
    tokens, remainder = _scanner.scan(input_string.strip())

    curr_indent = 0
    indent_stack = [0]
    newline_last = False
    inside_bracket = 0

    for tok in tokens:
        indent_change = 0

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
            position += tok.value
            newline_last = True
        else:
            tok.line = position
            newline_last = False

        # If indentation decreased we want to generate the needed dedent
        # tokens. These tokens are instantiated here as they cannot be
        # matched by regular expression.
        if indent_change < 0:
            while indent_stack[-1] > curr_indent:
                yield Dedent(indent_stack.pop(), line=position)
                yield NewLine(line=position)

        # If indentation increased we want to yield the indent token.
        if indent_change > 0:
            indent_stack.append(curr_indent)
            yield tok

        # We don't want to yield any other Indent tokens as our goal is
        # to represent the left/right braces with Indent/Dedent tokens.
        if tok.id != Indent.id and (not inside_bracket or
                                    tok.id != NewLine.id):
            yield tok

    yield End()


class tokenize(peekable):
    """Tokenizes an input string.

    :param input_string: String to be tokenized.
    :type input_string: str
    :return: List of pairs (token type, value).
    """

    def __init__(self, input_string):
        super(tokenize, self).__init__(_tokenize(input_string))

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
        tok = next(self)
        if skip is not None:
            while tok.id == skip.id:
                tok = next(self)
        if allowed is None:
            return tok
        try:
            allowed_tokens = iter(allowed)
        except TypeError:
            allowed_tokens = [allowed]
        if all(tok.id != Token.id for Token in allowed_tokens):
            msg = 'Unexpected token {!r}, expected {}, line {}.'
            tok_msg = ' or '.join([T.id for T in allowed_tokens])
            raise errors.SyntaxError(msg.format(tok, tok_msg, tok.line))
        return tok


def parse(input_string):
    """Parses given string according to NEON syntax.

    :param input_string: String to parse.
    :type input_string: string
    :return: Parsed string.
    :rtype: :class:`OrderedDict`
    """
    data = OrderedDict()
    tokens = tokenize(input_string)

    for tok in tokens:
        if tok.id != NewLine.id:
            break

    while tok.id != End.id:
        key = tok.parse(tokens)
        tokens.advance(Colon)
        tok = tokens.advance()

        if tok.id == NewLine.id:
            tok = tokens.advance()
        data[key] = tok.parse(tokens)

        tokens.advance(NewLine)
        tok = tokens.advance()

    return data


#: The Scanner is instantiated with a list of re's and associated
#: functions. It is used to scan a string, returning a list of parts
#: which match the given re's.
#:
#: See: http://stackoverflow.com/a/17214398/2874089
_scanner = re.Scanner([
    TokenClass.getscan() for TokenClass in TOKENS
    if TokenClass.re is not None
], flags=SCANNER_FLAGS)
