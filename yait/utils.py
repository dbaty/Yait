"""Various utilities.

$Id$
"""

from datetime import datetime
import re

from docutils.core import publish_parts
from docutils.writers.html4css1 import Writer


DOCUTILS_SETTINGS = {'output_encoding': 'utf-8',
                     'initial_header_level': 2}
TIME_REGEXP = re.compile('(?:(\d+)w)?'
                         ' ?(?:(\d+)d)?'
                         ' ?(?:(\d+)h)?'
                         ' ?(?:(\d+)m)?')
def strToTime(s):
    """Convert a string to a number of minutes.

    A day is supposed to have 8 hours. As well, a week has 5 days.

    >>> strToTime('')
    0
    >>> strToTime('0')
    0
    >>> strToTime('1m')
    1
    >>> strToTime('1h 25m')
    85
    >>> strToTime('1d')
    480
    >>> strToTime('1d 1h')
    540
    >>> strToTime('1d 1h 1m')
    541
    >>> strToTime('1w')
    2400
    """
    m = TIME_REGEXP.match(s)
    if m is None:
        return 0
    t = 0
    for i, j in zip(m.groups(), (2400, 480, 60, 1)):
        if i is not None:
            t += int(i) * j
    return t


def timeToStr(t):
    """Convert a number of minutes into a human-readable string.

    >>> timeToStr(0)
    ''
    >>> timeToStr(1)
    '1m'
    >>> timeToStr(59)
    '59m'
    >>> timeToStr(60)
    '1h'
    >>> timeToStr(61)
    '1h 1m'
    >>> timeToStr(479)
    '7h 59m'
    >>> timeToStr(480)
    '1d'
    >>> timeToStr(541)
    '1d 1h 1m'
    >>> timeToStr(2399)
    '4d 7h 59m'
    >>> timeToStr(2401)
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


def strToDate(s, format='dd/mm/yyyy'):
    """Convert a string to the date it respresents.

    Only one format is available: ``dd/mm/yyyy``.

    >>> strToDate('', 'yyyy/dd/mm')
    Traceback (most recent call last):
    ...
    ValueError: Unrecognized date format: yyyy/dd/mm
    >>> strToDate('', 'dd/mm/yyyy') is None
    True
    >>> from datetime import datetime
    >>> strToDate('28/07/2011') == datetime(2011, 07, 28)
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


def renderReST(text):
    """Render the given ``text`` through the reStructuredText engine.

    >>> renderReST('this is **bold**')
    u'<p>this is <strong>bold</strong></p>'
    """
    writer = Writer()
    parts = publish_parts(
        text, writer=writer, settings_overrides=DOCUTILS_SETTINGS)
    return parts['body'].strip()
