# -*- coding: utf-8 -*-


import re
from collections import OrderedDict

from .utils import lstripped, peekable, advance
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


def tokenize(input_string):
    """Tokenizes a string.

    :param input_string: String to be tokenized.
    :type input_string: str
    :return: List of pairs (token type, value).
    """
    return peekable(_tokenize(input_string))


def parse(input_string):
    """Parses given string according to NEON syntax.

    :param input_string: String to parse.
    :type input_string: string
    :return: Parsed string.
    :rtype: :class:`OrderedDict`
    """
    data = OrderedDict()
    tokens = peekable(tokenize(input_string))

    for tok in tokens:
        if tok.id != NewLine.id:
            break

    while tok.id != End.id:
        key = tok.parse(tokens)
        advance(tokens, Colon)
        tok = advance(tokens)

        if tok.id == NewLine.id:
            tok = advance(tokens)
        data[key] = tok.parse(tokens)

        advance(tokens, NewLine)
        tok = advance(tokens)

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
