# -*- coding: utf-8 -*-


import re
import dateutil.parser
from collections import OrderedDict

from . import errors
from .entity import Entity
from .utils import lstripped, variants, classproperty, peekable


#: Flags to use for the Scanner class.
SCANNER_FLAGS = re.MULTILINE | re.UNICODE | re.VERBOSE

#: List of all tokens.
TOKENS = []

#: Pattern for matching hexadecimal numbers.
PATTERN_HEX = re.compile(r'0x[0-9a-fA-F]+')


def token(cls):
    """Registers a token class.
    """
    assert issubclass(cls, Token), 'Tokens must subclass the Token class.'
    TOKENS.append(cls)
    return cls


def advance(tokens, allowed=None, skip_newlines=False):
    """Helper for iterating through tokens.

    :param tokens: List of tokens.
    :type tokens: iterable
    :param allowed: Optional list of allowed tokens. Default is any token.
        If the found token is not allowed, the function raises syntax error.
    :type allowed: :class:`Token` or iterable of tokens
    :param skip_newlines: If :obj:`True`, a sequence of new line
        tokens is skipped first. Default is :obj:`False`.
    :type skip_newlines: boolean
    """
    tok = next(tokens)
    if skip_newlines:
        while tok.id == NewLine.id:
            tok = next(tokens)
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


class Token(object):
    """Token representation.
    """
    #: Regular expression for tokenization.
    re = None

    @classproperty
    def id(cls):
        return cls.__name__

    def __init__(self, value=None, line=None):
        self.value = value
        self.line = line

    def parse(self, tokens):
        return self.value

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __str__(self):
        name = type(self).__name__
        value = '' if self.value is None else self.value
        return '{}({})'.format(name, value)

    def __repr__(self):
        return str(self)

    @classmethod
    def do(cls, scanner, string):
        return cls(string)

    @classmethod
    def getscan(cls):
        return (cls.re, cls.do)


class Primitive(Token):
    """Represents primitive type.
    """
    def parse(self, tokens):
        peek = tokens.peek()
        if peek.id == LeftRound.id:
            attributes = advance(tokens).parse(tokens)
            return Entity(self.value, attributes)
        return self.value


@token
class String(Primitive):
    """Represents string token.
    """
    re = r"""
          (?: "[^"\n]*" | '[^'\n]*' )
          """

    @classmethod
    def do(cls, scanner, string):
        double = '"'
        single = "'"
        if string[0] == double:
            string = string.strip(double)
        else:
            string = string.strip(single)
        return cls(string)


@token
class Integer(Primitive):
    """Represents integer token.
    """
    re = None

    @classmethod
    def convert(cls, string):
        try:
            if string.isdigit():
                return int(string)
            if PATTERN_HEX.match(string):
                return int(string, base=16)
        except ValueError:
            return


@token
class Float(Primitive):
    """Represents float token.
    """
    re = None

    @classmethod
    def convert(cls, string):
        try:
            return float(string)
        except ValueError:
            return


@token
class Boolean(Primitive):
    """Represents boolean token.
    """
    re = None

    _mapping = {
        True: variants('true', 'yes', 'on'),
        False: variants('false', 'no', 'off'),
    }

    @classmethod
    def convert(cls, string):
        for value, alternatives in cls._mapping.items():
            if string in alternatives:
                return value


@token
class NoneValue(Primitive):
    """Represents :obj:`None` token.
    """
    re = None

    _variants = variants('null')


@token
class DateTime(Primitive):
    """Represents datetime token.
    """
    re = None

    @classmethod
    def convert(cls, string):
        try:
            return dateutil.parser.parse(string)
        except ValueError:
            return


@token
class Literal(Token):
    """Represents literal token.
    """
    re = r"""
          (?: [^#"',:=[\]{}()\x00-\x20!`-] | [:-][^"',\]})\s] )
          (?: [^,:=\]})(\x00-\x20]+ | :(?! [\s,\]})] | $ ) |
              [\ \t]+ [^#,:=\]})(\x00-\x20] )*
          """

    @classmethod
    def do(cls, scanner, string):
        for Type in [Integer, Float, Boolean, DateTime]:
            value = Type.convert(string)
            if value is not None:
                return Type(value)
        if string in NoneValue._variants:
            return NoneValue(None)
        return String(string)


class Symbol(Token):
    """Represents symbol token.
    """

    @classmethod
    def do(cls, scanner, string):
        return cls()


@token
class Comma(Symbol):
    """Represents comma token.
    """
    re = r','


@token
class Colon(Symbol):
    """Represents colon token.
    """
    re = r':'


@token
class EqualSign(Symbol):
    """Represents equal sign.
    """
    re = r'='


@token
class Hyphen(Symbol):
    """Represents hyphen token.
    """
    re = r'-'


@token
class LeftRound(Symbol):
    """Represents left round bracket.
    """
    re = r'\('

    def parse(self, tokens):
        data = OrderedDict()
        tok = advance(tokens, skip_newlines=True)

        while tok.id != RightRound.id:
            key = tok.parse(tokens)
            advance(tokens, EqualSign)
            data[key] = advance(tokens).parse(tokens)

            tok = advance(tokens, (Comma, RightRound))
            if tok.id == Comma.id:
                tok = advance(tokens, skip_newlines=True)

        return data


@token
class RightRound(Symbol):
    """Represents right round bracket.
    """
    re = r'\)'


@token
class LeftSquare(Symbol):
    """Represents left square bracket.
    """
    re = r'\['

    def parse(self, tokens):
        data = []
        tok = advance(tokens, skip_newlines=True)

        while tok.id != RightSquare.id:
            value = tok.parse(tokens)
            data.append(value)

            tok = advance(tokens, (Comma, RightSquare))
            if tok.id == Comma.id:
                tok = advance(tokens, skip_newlines=True)

        return data


@token
class RightSquare(Symbol):
    """Represents right square bracket.
    """
    re = r'\]'


@token
class LeftBrace(Symbol):
    """Represents left brace.
    """
    re = r'{'

    def parse(self, tokens):
        data = OrderedDict()
        tok = advance(tokens, skip_newlines=True)

        while tok.id != RightBrace.id:
            key = tok.parse(tokens)
            advance(tokens, Colon)
            data[key] = advance(tokens).parse(tokens)

            tok = advance(tokens, (Comma, RightBrace))
            if tok.id == Comma.id:
                tok = advance(tokens, skip_newlines=True)

        return data


@token
class RightBrace(Symbol):
    """Represents right brace.
    """
    re = r'}'


@token
class Comment(Token):
    """Represents comment token.
    """
    re = r'\#.*'
    do = None  # ignore comments


@token
class Indent(Token):
    """Represents indent token.
    """
    re = r'^[\t\ ]+'

    def _parse_list(self, tokens):
        data = []
        tok = advance(tokens)

        while tok.id != Dedent.id:
            value = advance(tokens).parse(tokens)
            data.append(value)
            advance(tokens, NewLine)
            tok = advance(tokens, (Hyphen, Dedent))

        return data

    def _parse_dict(self, tokens):
        data = {}
        tok = advance(tokens)

        while tok.id != Dedent.id:
            key = tok.parse(tokens)
            advance(tokens, Colon)
            tok = advance(tokens)

            if tok.id == NewLine.id:
                tok = advance(tokens)
            data[key] = tok.parse(tokens)

            advance(tokens, NewLine)
            tok = advance(tokens)

        return data

    def parse(self, tokens):
        tok = tokens.peek()

        if tok.id == Hyphen.id:
            return self._parse_list(tokens)
        else:
            return self._parse_dict(tokens)

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class Dedent(Token):
    """Represents dedent token.
    """
    re = None  # this token is generated after the scanning procedure


@token
class NewLine(Token):
    """Represents new line token.
    """
    re = r'[\n]+'

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class WhiteSpace(Token):
    """Represents comment token.
    """
    re = r'[\t\ ]+'
    do = None  # ignore white-spaces


@token
class Unknown(Token):
    """Represents unknown character sequence match.
    """
    re = r'.*'

    @classmethod
    def do(cls, scanner, token):
        msg = 'Unknown character sequence: {!r}'
        raise errors.TokenError(msg.format(token))


@token
class End(Token):
    """Represents end token.
    """
    re = None


#: The Scanner is instantiated with a list of re's and associated
#: functions. It is used to scan a string, returning a list of parts
#: which match the given re's.
#:
#: See: http://stackoverflow.com/a/17214398/2874089
_scanner = re.Scanner([
    TokenClass.getscan() for TokenClass in TOKENS
    if TokenClass.re is not None
], flags=SCANNER_FLAGS)
