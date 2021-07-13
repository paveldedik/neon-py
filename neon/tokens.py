# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import re

import dateutil.parser

from . import errors
from ._compat import OrderedDict
from .entity import Entity
from .utils import camel_case_to_underscore, classproperty, variants

#: List of all tokens.
TOKENS = []

#: Pattern for matching hexadecimal numbers.
PATTERN_HEX = re.compile(r"0x[0-9a-fA-F]+")


def token(cls):
    """Registers a token class."""
    assert issubclass(cls, Token), "Tokens must subclass the Token class."
    TOKENS.append(cls)
    return cls


class Token(object):
    """Token representation."""

    #: Regular expression for tokenization.
    re = None

    @classproperty
    def id(cls):
        return cls

    @classproperty
    def name(cls):
        return camel_case_to_underscore(cls.__name__).replace("_", " ")

    def __init__(self, value=None, line=None):
        self.value = value
        self.line = line

    def parse(self, tokens):
        return self.value

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __str__(self):
        name = type(self).__name__
        value = "" if self.value is None else self.value
        return "{}({})".format(name, value)

    def __repr__(self):
        return str(self)

    @classmethod
    def do(cls, scanner, string):
        return cls(string)

    @classmethod
    def getscan(cls):
        return (cls.re, cls.do)


class Primitive(Token):
    """Represents primitive type."""

    def parse(self, tokens):
        peek = tokens.peek()
        if peek.id == LeftRound.id:
            attributes = tokens.advance().parse(tokens)
            return Entity(self.value, attributes)
        return self.value


@token
class String(Primitive):
    """Represents string token."""

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
    """Represents integer token."""

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
    """Represents float token."""

    re = None

    @classmethod
    def convert(cls, string):
        try:
            return float(string)
        except ValueError:
            return


@token
class Boolean(Primitive):
    """Represents boolean token."""

    re = None

    _mapping = {
        True: variants("true", "yes", "on"),
        False: variants("false", "no", "off"),
    }

    @classmethod
    def convert(cls, string):
        for value, alternatives in cls._mapping.items():
            if string in alternatives:
                return value


@token
class NoneValue(Primitive):
    """Represents :obj:`None` token."""

    re = None

    _variants = variants("null")


@token
class DateTime(Primitive):
    """Represents datetime token."""

    re = None

    @classmethod
    def convert(cls, string):
        try:
            return dateutil.parser.parse(string)
        except (ValueError, TypeError):
            return


@token
class Literal(Token):
    """Represents literal token."""

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
    """Represents symbol token."""

    @classproperty
    def name(cls):
        return "'{}'".format(str(cls.re).replace("\\", ""))

    @classmethod
    def do(cls, scanner, string):
        return cls()


@token
class Comma(Symbol):
    """Represents comma token."""

    re = r","


@token
class Colon(Symbol):
    """Represents colon token."""

    re = r":"


@token
class EqualSign(Symbol):
    """Represents equal sign."""

    re = r"="


@token
class Hyphen(Symbol):
    """Represents hyphen token."""

    re = r"-"


@token
class LeftRound(Symbol):
    """Represents left round bracket."""

    re = r"\("

    def parse(self, tokens):
        data = OrderedDict()
        tok = tokens.advance(skip=NewLine)
        iteration = 0

        while tok.id != RightRound.id:
            key = tok.parse(tokens)
            tok = tokens.advance((EqualSign, Comma, RightRound))

            if tok.id == EqualSign.id:
                data[key] = tokens.advance().parse(tokens)
                tok = tokens.advance((Comma, RightRound))
                if tok.id == Comma.id:
                    tok = tokens.advance(skip=NewLine)

            elif tok.id == Comma.id:
                data[iteration] = key
                tok = tokens.advance(skip=NewLine)

            elif tok.id == RightRound.id:
                data[iteration] = key

            iteration += 1

        return data


@token
class RightRound(Symbol):
    """Represents right round bracket."""

    re = r"\)"


@token
class LeftSquare(Symbol):
    """Represents left square bracket."""

    re = r"\["

    def parse(self, tokens):
        data = []
        tok = tokens.advance(skip=NewLine)

        while tok.id != RightSquare.id:
            value = tok.parse(tokens)
            data.append(value)

            tok = tokens.advance((Comma, RightSquare))
            if tok.id == Comma.id:
                tok = tokens.advance(skip=NewLine)

        return data


@token
class RightSquare(Symbol):
    """Represents right square bracket."""

    re = r"\]"


@token
class LeftBrace(Symbol):
    """Represents left brace."""

    re = r"{"

    def parse(self, tokens):
        data = OrderedDict()
        tok = tokens.advance(skip=NewLine)

        while tok.id != RightBrace.id:
            key = tok.parse(tokens)
            tokens.advance(Colon)
            data[key] = tokens.advance().parse(tokens)

            tok = tokens.advance((Comma, RightBrace))
            if tok.id == Comma.id:
                tok = tokens.advance(skip=NewLine)

        return data


@token
class RightBrace(Symbol):
    """Represents right brace."""

    re = r"}"


@token
class Comment(Token):
    """Represents comment token."""

    re = r"\#.*"
    do = None  # ignore comments


@token
class Indent(Token):
    """Represents indent token."""

    re = r"^[\t\ ]+"

    def _parse_list(self, tokens):
        data = []
        tok = tokens.advance()

        while tok.id not in [Dedent.id, End.id]:
            if tokens.peek().id == NewLine.id:
                value = None
            else:
                tok = tokens.advance()
                if tokens.peek().id == Colon.id:
                    tokens.advance()
                    key = tok.parse(tokens)
                    tok = tokens.advance(skip=NewLine)
                    value = {key: tok.parse(tokens)}
                else:
                    value = tok.parse(tokens)
            data.append(value)

            tok = tokens.advance((End, NewLine, Dedent))
            if tok.id == NewLine.id:
                tok = tokens.advance((Hyphen, Dedent))

        return data

    def _parse_dict(self, tokens, tok=None):
        data = OrderedDict()
        tok = tok or tokens.advance()

        while tok.id not in [Dedent.id, End.id]:
            key = tok.parse(tokens)
            tokens.advance(Colon)

            tok = tokens.advance()
            if tok.id == NewLine.id:
                tok = tokens.advance()
                if tok.id not in [Indent.id, Dedent.id]:
                    data[key] = None
                    continue
            data[key] = tok.parse(tokens)

            tok = tokens.advance((End, NewLine, Dedent))
            if tok.id == NewLine.id:
                tok = tokens.advance(skip=NewLine)

        return data

    def parse(self, tokens):
        peek = tokens.peek()

        while peek.id == NewLine.id:
            tokens.advance()
            peek = tokens.peek()

        if peek.id == Hyphen.id:
            return self._parse_list(tokens)
        else:
            return self._parse_dict(tokens)

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class Dedent(Token):
    """Represents dedent token."""

    re = None  # this token is generated after the scanning procedure


@token
class NewLine(Token):
    """Represents new line token."""

    re = r"[\n]+"

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class WhiteSpace(Token):
    """Represents comment token."""

    re = r"[\t\ ]+"
    do = None  # ignore white-spaces


@token
class Unknown(Token):
    """Represents unknown character sequence match."""

    re = r".*"

    @classmethod
    def do(cls, scanner, token):
        msg = "Unknown character sequence: {!r}"
        raise errors.TokenError(msg.format(token))


@token
class End(Token):
    """Represents EOL token."""

    re = None
    name = "end of file"
