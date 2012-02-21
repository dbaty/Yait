from datetime import datetime
import re

TIME_REGEXP = re.compile('(?:(\d+)w)?'
                         ' ?(?:(\d+)d)?'
                         ' ?(?:(\d+)h)?'
                         ' ?(?:(\d+)m)?')
def str_to_time(s):
    """Convert a string to a number of minutes.

    A day is supposed to have 8 hours. As well, a week has 5 days.

    >>> str_to_time('1t')
    Traceback (most recent call last):
    ...
    ValueError: Wrong time format: 1t
    >>> str_to_time('')
    0
    >>> str_to_time('0')
    0
    >>> str_to_time('1m')
    1
    >>> str_to_time('1h 25m')
    85
    >>> str_to_time('1d')
    480
    >>> str_to_time('1d 1h')
    540
    >>> str_to_time('1d 1h 1m')
    541
    >>> str_to_time('1w')
    2400
    """
    if s in (None, '', '0'):
        return 0
    matches = TIME_REGEXP.match(s).groups()
    if not any(matches):
        raise ValueError('Wrong time format: %s' % s)
    t = 0
    for i, j in zip(matches, (2400, 480, 60, 1)):
        if i is not None:
            t += int(i) * j
    return t


def time_to_str(t):
    """Convert a number of minutes into a human-readable string.

    >>> time_to_str(0)
    ''
    >>> time_to_str(1)
    '1m'
    >>> time_to_str(59)
    '59m'
    >>> time_to_str(60)
    '1h'
    >>> time_to_str(61)
    '1h 1m'
    >>> time_to_str(479)
    '7h 59m'
    >>> time_to_str(480)
    '1d'
    >>> time_to_str(541)
    '1d 1h 1m'
    >>> time_to_str(2399)
    '4d 7h 59m'
    >>> time_to_str(2401)
    '1w 1m'
    """
    s = ''
    for c, u in zip((2400, 480, 60, 1),
                    ('w', 'd', 'h', 'm')):
        q = t / c
        t = t - (q * c)
        if q:
            s += ' %d%s' % (q, u)
    s = s.lstrip()
    return s


def str_to_date(s, format='dd/mm/yyyy'): ## FIXME: is it used anywhere?
    """Convert a string to the date it respresents.

    Only one format is available: ``dd/mm/yyyy``.

    >>> str_to_date('', 'yyyy/dd/mm')
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized date format: yyyy/dd/mm
    >>> str_to_date('', 'dd/mm/yyyy') is None
    True
    >>> from datetime import datetime
    >>> str_to_date('28/07/2011') == datetime(2011, 07, 28)
    True
    """
    if format != 'dd/mm/yyyy':
        raise ValueError('Unrecognized date format: %s' % format)
    ## FIXME: add error handling
    if not s:
        return None
    components = map(int, s.split('/'))
    components.reverse()
    return datetime(*components)
