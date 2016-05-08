# -*- coding: utf-8 -*-


import itertools

from . import errors


_marker = object()


class classproperty(object):
    """Useful when class properties need to be defined."""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        return self.fget(cls)


def lstripped(string):
    """Number of potentially stripped characters on left.

    :return: A string of characters that will be stripped
        on the left side of the given string if the method
        `strip()` is called on it.
    :rtype: string
    """
    return ''.join(itertools.takewhile(str.isspace, string))


def variants(*strings):
    """Creates three variants of each string:

    - lowercase (e.g. `husky`)
    - title version (e.g. `Husky`)
    - uppercase (e.g. `HUSKY`)

    :return: A list of all variants of all given strings.
    :rtype: list
    """
    result = []
    for string in strings:
        lowercase = string.lower()
        result += [lowercase, lowercase.title(), string.upper()]
    return result


def advance(tokens, allowed=None, skip=None):
    """Helper for iterating through tokens.

    :param tokens: List of tokens.
    :type tokens: iterable
    :param allowed: Optional list of allowed tokens. Default is any token.
        If the found token is not allowed, the function raises syntax error.
    :type allowed: :class:`Token` or iterable of tokens
    :param skip: If :obj:`True`, a sequence of given token types
        is skipped first. Default is :obj:`False`.
    :type skip: boolean
    """
    tok = next(tokens)
    if skip is not None:
        while tok.id == skip.id:
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


class peekable(object):
    """Wrapper for an iterator to allow 1-item lookahead
    Call ``peek()`` on the result to get the value that will next pop out of
    ``next()``, without advancing the iterator:
        >>> p = peekable(xrange(2))
        >>> p.peek()
        0
        >>> p.next()
        0
        >>> p.peek()
        1
        >>> p.next()
        1
    Pass ``peek()`` a default value, and it will be returned in the case where
    the iterator is exhausted:
        >>> p = peekable([])
        >>> p.peek('hi')
        'hi'
    If no default is provided, ``peek()`` raises ``StopIteration`` when there
    are no items left.
    To test whether there are more items in the iterator, examine the
    peekable's truth value. If it is truthy, there are more items.
        >>> assert peekable(xrange(1))
        >>> assert not peekable([])

    .. NOTE:: Taken from: https://github.com/erikrose/more-itertools
    """
    # Lowercase to blend in with itertools. The fact that it's a class is an
    # implementation detail.

    def __init__(self, iterable):
        self._it = iter(iterable)

    def __iter__(self):
        return self

    def __nonzero__(self):
        try:
            self.peek()
        except StopIteration:
            return False
        return True

    def peek(self, default=_marker):
        """Return the item that will be next returned from ``next()``.
        Return ``default`` if there are no items left. If ``default`` is not
        provided, raise ``StopIteration``.
        """
        if not hasattr(self, '_peek'):
            try:
                self._peek = self._it.next()
            except StopIteration:
                if default is _marker:
                    raise
                return default
        return self._peek

    def next(self):
        ret = self.peek()
        del self._peek
        return ret
