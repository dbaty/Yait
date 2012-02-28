from datetime import datetime
import re

TIME_REGEXP = re.compile('(?:(\d+)w)?'
                         ' *(?:(\d+)d)?'
                         ' *(?:(\d+)h)?'
                         ' *(?:(\d+)m)?')


def str_to_time(s):
    """Convert a string to a number of minutes.

    A day is supposed to have 8 hours. As well, a week has 5 days.
    """
    if s in (None, '', '0'):
        return 0
    s = s.strip()
    matches = TIME_REGEXP.match(s).groups()
    if not any(matches):
        raise ValueError('Wrong time format: %s' % s)
    t = 0
    for i, j in zip(matches, (2400, 480, 60, 1)):
        if i is not None:
            t += int(i) * j
    return t


def time_to_str(t):
    """Convert a number of minutes into a human-readable string."""
    s = ''
    for c, u in zip((2400, 480, 60, 1),
                    ('w', 'd', 'h', 'm')):
        q = t / c
        t = t - (q * c)
        if q:
            s += ' %d%s' % (q, u)
    s = s.lstrip()
    return s


def str_to_date(s, format='dd/mm/yyyy'):  # FIXME: is it used anywhere?
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
