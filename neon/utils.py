# -*- coding: utf-8 -*-


from __future__ import unicode_literals

import re
import itertools

from ._compat import unicode


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
    return ''.join(itertools.takewhile(unicode.isspace, string))


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


def camel_case_to_underscore(name):
    """Converts string from camel case notation to underscore.

    :param name: String to convert to underscore.
    :type name: string
    :return: A string converted from camel case to underscore.
    :rtype: string
    """
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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

    _marker = object()

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
                self._peek = next(self._it)
            except StopIteration:
                if default is self._marker:
                    raise
                self._peek = self._marker
        return self._peek

    def next(self):
        ret = self.peek()
        del self._peek
        return ret
