r"""Converters from :class:`str` to another type.

These functions can be used for the ``type`` parameter in methods of
:class:`~argparse.ArgumentParser` and :class:`~argparsebuilder.ArgParseBuilder`
or similar use cases.

All functions raise :class:`ValueError`\ s if the string cannot be converted.
"""

import datetime as dt
import locale
from importlib.resources import read_text

__version__ = read_text(__package__, 'VERSION').strip()

__all__ = ['booleans', 'use_locale_default', 'boolean', 'int_conv',
           'float_conv', 'factor_conv', 'duration', 'datetime', 'date', 'time']

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


def boolean(string, values=None):
    """Convert a string to a boolean value.

    The ``string`` is converted to lower case before
    looking up the boolean value in ``values`` or :data:`booleans`
    (if ``values`` is ``None``).

    :param str string: input string
    :value dict: mapping from strings to booleans
    :return: converted value
    :rtype: bool
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


def factor_conv(string, *, conv=None, factors=None):
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
    """
    for sym in factors:
        if string.endswith(sym):
            if sym:
                return conv(string[:-len(sym)]) * factors[sym]
            else:
                return conv(string) * factors[sym]
    raise ValueError(f'invalid value: {string!r}')


def datetime(string, format=None):
    """Convert a string to a :class:`datetime.datetime`.

    If ``format=None`` this function uses
    :meth:`datetime.datetime.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: datetime string
    :param format: format string
    :type format: str or None
    :return: converted datetime
    :rtype: datetime.datetime
    """
    if format is None:
        return dt.datetime.fromisoformat(string)
    else:
        return dt.datetime.strptime(string, format)


def date(string, format=None):
    """Convert a string to a class:`datetime.date`.

    If ``format=None`` this function uses
    :meth:`datetime.date.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: date string
    :param format: format string
    :return: converted date
    :rtype: datetime.date
    """
    if format is None:
        return dt.date.fromisoformat(string)
    else:
        return dt.datetime.strptime(string, format).date()


def time(string, format=None):
    """Convert a string to a :class:`datetime.time`.

    If ``format=None`` this function uses
    :meth:`datetime.time.fromisoformat` else
    :meth:`datetime.datetime.strptime`.

    :param str string: time string
    :param format: format string
    :return: converted time
    :rtype: datetime.time
    """
    if format is None:
        return dt.time.fromisoformat(string)
    else:
        return dt.datetime.strptime(string, format).time()


def duration(string, use_locale=None):
    """Convert duration string to seconds.

    Format: [[H:]M:]S[.f]

    See also: :func:`salmagundi.strings.parse_timedelta`

    :param str string: duration string
    :param use_locale: ``True`` use current locale; ``None`` use
                       :data:`use_locale_default`
    :type use_locale: bool or None
    :return: converted duration
    :rtype: float

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
