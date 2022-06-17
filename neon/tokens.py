import functools

import dateutil.parser

from . import errors
from .entity import Entity
from .utils import camel_case_to_underscore, classproperty, variants

#: List of all tokens.
TOKENS = []


def token(cls):
    """Registers a token class."""
    assert issubclass(cls, Token), "Tokens must subclass the Token class."
    TOKENS.append(cls)
    return cls


class Token(object):
    """Token representation."""

    #: Regular expression for tokenization.
    re = None

    #: Unique ID of the token.
    id = None

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
          (?: "(?:\\.|[^"\\])*" | '(?:\\.|[^'\\])*' )
          """
    id = "str"

    @classmethod
    def do(cls, scanner, string):
        double = '"'
        single = "'"
        if string[0] == double:
            string = string.strip(double).replace(r"\"", '"')
        else:
            string = string.strip(single).replace(r"\'", "'")
        # TODO: refactor to deal with \t, \n, \r, \xXX, \uXXXX etc
        string = string.replace("\\\\", "\\")
        return cls(string)


@token
class Integer(Primitive):
    """Represents integer token."""

    re = None
    id = "int"

    @classmethod
    def convert(cls, string):
        try:
            return int(string, 0)
        except ValueError:
            return


@token
class Float(Primitive):
    """Represents float token."""

    re = None
    id = "float"

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
    id = "bool"

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
    id = "none"

    _variants = variants("null")


@token
class DateTime(Primitive):
    """Represents datetime token."""

    re = None
    id = "datetime"

    @classmethod
    @functools.lru_cache(maxsize=None)
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
    id = "literal"

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

    id = "symbol"

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
    id = "comma"


@token
class Colon(Symbol):
    """Represents colon token."""

    re = r":"
    id = "colon"


@token
class EqualSign(Symbol):
    """Represents equal sign."""

    re = r"="
    id = "eq"


@token
class Hyphen(Symbol):
    """Represents hyphen token."""

    re = r"-"
    id = "hyphen"


@token
class LeftRound(Symbol):
    """Represents left round bracket."""

    re = r"\("
    id = "leftround"

    def parse(self, tokens):
        data = {}
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
    id = "rightround"


@token
class LeftSquare(Symbol):
    """Represents left square bracket."""

    re = r"\["
    id = "leftsquare"

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
    id = "rightsquare"


@token
class LeftBrace(Symbol):
    """Represents left brace."""

    re = r"{"
    id = "leftbrace"

    def parse(self, tokens):
        data = {}
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
    id = "rightbrace"


@token
class Comment(Token):
    """Represents comment token."""

    re = r"\s*\#.*"
    id = "comment"
    do = None  # ignore comments


@token
class Indent(Token):
    """Represents indent token."""

    re = r"^[\t\ ]+"
    id = "indent"

    def _parse_list(self, tokens, tok):
        data = []

        while tok.id not in [Dedent.id, End.id]:
            while tok.id == Hyphen.id:
                old_tok = tok
                tok = tokens.advance(skip=(NewLine, Indent))
                # in this case, the list looks like this:
                # -
                # - a
                if old_tok.id == tok.id == Hyphen.id:
                    data.append(None)
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

    def _parse_dict(self, tokens, tok):
        data = {}

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
        tok = tokens.advance()

        while tok.id == NewLine.id:
            tok = tokens.advance()

        if tok.id == Hyphen.id:
            return self._parse_list(tokens, tok)
        elif tokens.peek().id == End.id:
            return tok.parse(tokens)
        else:
            return self._parse_dict(tokens, tok)

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class Dedent(Token):
    """Represents dedent token."""

    re = None  # this token is generated after the scanning procedure
    id = "dedent"


@token
class NewLine(Token):
    """Represents new line token."""

    re = r"[\n]+"
    id = "newline"

    @classmethod
    def do(cls, scanner, string):
        return cls(len(string))


@token
class WhiteSpace(Token):
    """Represents comment token."""

    re = r"[\t\ ]+"
    id = "whitespace"
    do = None  # ignore white-spaces


@token
class Unknown(Token):
    """Represents unknown character sequence match."""

    re = r".*"
    id = "unknown"

    @classmethod
    def do(cls, scanner, token):
        msg = "Unknown character sequence: {!r}"
        raise errors.TokenError(msg.format(token))


@token
class End(Token):
    """Represents EOL token."""

    re = None
    id = "end"
    name = "end of file"
