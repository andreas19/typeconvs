r"""Converters from :class:`str` to another type.

These functions can be used for the ``type`` parameter in methods of
:class:`~argparse.ArgumentParser` and :class:`~argparsebuilder.ArgParseBuilder`
or similar use cases (if necessary in combination with
:func:`functools.partial`).
"""

import locale
import re
from datetime import datetime, date, time
from importlib.resources import read_text
from operator import le, ge

__version__ = read_text(__package__, 'VERSION').strip()

__all__ = ['booleans', 'use_locale_default', 'bool_conv', 'int_conv',
           'float_conv', 'factor_conv', 'duration', 'datetime_conv',
           'date_conv', 'time_conv', 'range_conv', 'sequence']

use_locale_default = False
"""Default value for :func:`int_conv` and :func:`float_conv`
for parameter ``use_locale``."""

booleans = {
    'false': False,
    'f': False,
    'no': False,
    'n': False,
    '0': False,
    'off': False,
    'true': True,
    't': True,
    'yes': True,
    'y': True,
    '1': True,
    'on': True,
}  #: Mapping from strings to boolean values.


def bool_conv(string, *, values=None):
    """Convert a string to a boolean value.

    The ``string`` is converted to lower case before
    looking up the boolean value in ``values`` or :data:`booleans`
    (if ``values`` is ``None``).

    :param str string: input string
    :value dict: mapping from strings to booleans
    :return: converted value
    :rtype: bool
    :raises ValueError: if the string cannot be converted

    .. versionchanged:: 0.2.0 Renamed (old name: boolean)
    """
    if values is None:
        values = booleans
    try:
        return values[string.lower()]
    except KeyError:
        raise ValueError(f'invalid boolean: {string!r}') from None


def int_conv(string, *, base=10, pred=None, use_locale=None):
    """Convert a string to an integer value.

    >>> import locale
    >>> locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    'de_DE.UTF-8'
    >>> int_conv('1.234', use_locale=True)
    1234
    >>> locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    'en_US.UTF-8'
    >>> int_conv('1,234', use_locale=True)
    1234
    >>> int_conv('-1', pred=lambda x: x > 0)
    Traceback (most recent call last):
      ...
    ValueError: invalid value: '-1'

    See :class:`int` for an explanation of parameter ``base``.

    :param str string: input string
    :param int base: base (>= 2 and <= 36, or 0)
    :param pred: predicate function
    :param use_locale: ``True`` use current locale; ``None`` use
                       :data:`use_locale_default`
    :type use_locale: bool or None
    :return: converted value
    :rtype: int
    :raises ValueError: if the string cannot be converted
    """
    if (use_locale if use_locale is not None else use_locale_default):
        string = locale.delocalize(string)
    x = int(string, base=base)
    if not pred or pred(x):
        return x
    raise ValueError(f'invalid value: {string!r}')


def float_conv(string, *, base=10, pred=None, use_locale=None):
    """Convert a string to a float value.

    :param str string: input string
    :param int base: base (>= 2 and <= 36, or 0)
    :param pred: predicate function
    :param use_locale: ``True`` use current locale; ``None`` use
                       :data:`use_locale_default`
    :type use_locale: bool or None
    :return: converted value
    :rtype: float
    :raises ValueError: if the string cannot be converted
    """
    if (use_locale if use_locale is not None else use_locale_default):
        string = locale.delocalize(string)
    if base != 10:
        if not (base == 0 or 2 <= base <= 36):
            raise ValueError('base must be >= 2 and <= 36, or 0')
        a, *b = string.rsplit('.', 1)
        try:
            if b:
                if base == 0:
                    prefix = a[:2].lower()
                    if prefix == '0b':
                        devisor = 2**(len(b[0]))
                    elif prefix == '0o':
                        devisor = 8**(len(b[0]))
                    elif prefix == '0x':
                        devisor = 16**(len(b[0]))
                    else:
                        devisor = 1
                else:
                    prefix = ''
                    devisor = base**(len(b[0]))
                frac = int(prefix + b[0], base=base) / devisor
            else:
                frac = 0.0
            x = int(a, base=base) + frac
        except ValueError:
            raise ValueError(
                f'could not convert string to float: {string!r}') from None
    else:
        x = float(string)
    if not pred or pred(x):
        return x
    raise ValueError(f'invalid value: {string!r}')


def factor_conv(string, *, conv, factors):
    """Convert a string with a factor.

    The symbols from ``factors`` are compared to the end of ``string``
    until one matches. The ``string`` is then shortend by the the length
    of the symbol and the rest converted with ``conv`` and multiplied by
    the factor that corresponds to the symbol.

    >>> factors = {'h': 3600, 'm': 60, 's': 1}
    >>> factor_conv('10m', conv=int, factors=factors)
    600

    :param str string: input string
    :param conv: converter function
    :param dict factors: mapping from symbol to factor
    :return: converted value
    :raises ValueError: if the string cannot be converted
    """
    for sym in factors:
        if string.endswith(sym):
            if sym:
                return conv(string[:-len(sym)]) * factors[sym]
            else:
                return conv(string) * factors[sym]
    raise ValueError(f'invalid value: {string!r}')


def datetime_conv(string, *, format=None):
    """Convert a string to a :class:`datetime.datetime`.

    If ``format=None`` this function uses
    :meth:`datetime.datetime.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: datetime string
    :param format: format string
    :type format: str or None
    :return: converted datetime
    :rtype: datetime.datetime
    :raises ValueError: if the string cannot be converted

    .. versionchanged:: 0.2.0 Renamed (old name: datetime)
    """
    if format is None:
        return datetime.fromisoformat(string)
    else:
        return datetime.strptime(string, format)


def date_conv(string, *, format=None):
    """Convert a string to a class:`datetime.date`.

    If ``format=None`` this function uses
    :meth:`datetime.date.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: date string
    :param format: format string
    :return: converted date
    :rtype: datetime.date
    :raises ValueError: if the string cannot be converted

    .. versionchanged:: 0.2.0 Renamed (old name: date)
    """
    if format is None:
        return date.fromisoformat(string)
    else:
        return datetime.strptime(string, format).date()


def time_conv(string, *, format=None):
    """Convert a string to a :class:`datetime.time`.

    If ``format=None`` this function uses
    :meth:`datetime.time.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: time string
    :param format: format string
    :return: converted time
    :rtype: datetime.time
    :raises ValueError: if the string cannot be converted

    .. versionchanged:: 0.2.0 Renamed (old name: time)
    """
    if format is None:
        return time.fromisoformat(string)
    else:
        return datetime.strptime(string, format).time()


def duration(string, *, use_locale=None):
    """Convert duration string to seconds.

    Format: [[H:]M:]S[.f]

    See also: :func:`salmagundi.strings.parse_timedelta`

    :param str string: duration string
    :param use_locale: ``True`` use current locale; ``None`` use
                       :data:`use_locale_default`
    :type use_locale: bool or None
    :return: converted duration
    :rtype: float
    :raises ValueError: if the string cannot be converted

    .. versionchanged:: 0.1.1 Add parameter ``use_locale``
    """
    h, m, s = 0, 0, 0
    a = string.split(':')
    try:
        s = float_conv(a[-1], pred=lambda x: 0.0 <= x < 60.0,
                       use_locale=use_locale)
        if len(a) >= 2:
            m = int_conv(a[-2], pred=lambda x: 0 <= x < 60)
        if len(a) == 3:
            h = int_conv(a[0], pred=lambda x: 0 <= x, use_locale=use_locale)
        if len(a) > 3:
            raise ValueError
    except ValueError:
        raise ValueError(f'invalid duration: {string!r}')
    return h * 3600.0 + m * 60.0 + s


_num_re = r'(?:\d(?:\.\d*)*)+'
_range_re = (fr'^\s*(?P<start>[-+]?{_num_re})\s*%s\s*'
             fr'(?P<end>[-+]?{_num_re})'
             fr'(?:\s*/\s*(?P<step>[-+]?{_num_re}))?\s*$')


def range_conv(string, *, conv=None, separator='-'):
    """Convert a range string.

    Range string: '<start><separator><end>[/<step>]' (default: <step> = 1)

    >>> list(range_conv('-2-4'))
    [-2, -1, 0, 1, 2, 3, 4]

    >>> list(range_conv('-2-4/2'))
    [-2, 0, 2, 4]

    >>> list(range_conv('4--2/-2'))
    [4, 2, 0, -2]

    >>> list(range_conv('4..-2/-2', separator='..'))
    [4, 2, 0, -2]

    >>> from itertools import chain
    >>> list(chain.from_iterable(sequence('1, -2-4/2, 42', conv=range_conv)))
    [1, -2, 0, 2, 4, 42]

    :param str string: input string
    :param conv: converter function which returns an int or a float value
                 (default: ``int``)
    :param str separator: separator between <start> and <end>
    :return: generator that yields converted values
    :raises ValueError: if the string cannot be converted

    .. versionadded:: 0.2.0

    .. versionchanged:: 0.2.1 Add parameter ``separator``
    """
    if not conv:
        conv = int
    if m := re.match(_range_re % re.escape(separator), string):
        start = conv(m['start'])
        if not isinstance(start, (int, float)):
            raise ValueError('conv must return int or float')
        if m['step']:
            step = conv(m['step'])
            if not step:
                raise ValueError('step cannot be zero')
        else:
            step = 1 if isinstance(start, int) else 1.0
        end = conv(m['end'])
        cmp = le if step > 0 else ge
        x = start
        while cmp(x, end):
            yield x
            x += step
    else:
        yield conv(string)


def sequence(string, *, conv=None, separator=','):
    """Convert a sequence string.

    >>> sequence('1, 2, 3', conv=float)
    (1.0, 2.0, 3.0)

    :param str string: input string
    :param conv: converter function
    :param str separator: separator between elements of sequence
    :return: generator that yields converted values
    :raises ValueError: if the string cannot be converted

    .. versionadded:: 0.2.0
    """
    for s in string.split(separator):
        yield conv(s)
