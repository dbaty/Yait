"""Text-related utilities."""

import re


RENDERERS = {}
try:
    import docutils  # pyflakes: ignore
    RENDERERS['rest'] = 'placeholder'
except ImportError:  # pragma: no cover
    # FIXME: log info
    pass


def render(src, renderer_name='rest'):
    """Render the given ``src`` text with the requested renderer."""
    renderer = RENDERERS.get(renderer_name)
    if renderer is None:
        # FIXME: log error
        return src
    return renderer(src)


PARAGRAPHS_SEPARATOR = re.compile('\n\n')

def render_plain(text):
    """Render the given ``text`` as plain text.

    Single lines are separated by ``<br/>`` tags. When an empty line
    is found, a paragraph (``<p>``) is generated.
    """
    text = text.replace('\r', '')
    paragraphs = PARAGRAPHS_SEPARATOR.split(text)
    text = ''.join(['<p>%s</p>' % p for p in paragraphs if p])
    text = text.replace('\n', '<br/>')
    return text

RENDERERS['plain'] = render_plain


if RENDERERS['rest']:
    from docutils.core import publish_parts
    from docutils.writers.html4css1 import Writer

    DOCUTILS_SETTINGS = {'output_encoding': 'utf-8',
                         'initial_header_level': 2}

    def render_rest(text):
        """Render the given ``text`` through the reStructuredText
        engine.
        """
        writer = Writer()
        parts = publish_parts(
            text, writer=writer, settings_overrides=DOCUTILS_SETTINGS)
        return parts['body'].strip()

    RENDERERS['rest'] = render_rest
