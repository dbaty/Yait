"""Text-related utilities."""

RENDERERS = {}
try:
    import docutils  # pyflakes: ignore
    RENDERERS['rest'] = 'placeholder'
except ImportError:
    # FIXME: log info
    pass


def render(src, renderer_name='rest'):
    """Render the given ``src`` text with the requested renderer."""
    renderer = RENDERERS.get(renderer_name)
    if renderer is None:
        # FIXME: log error
        return src
    return renderer(src)


if RENDERERS['rest']:
    from docutils.core import publish_parts
    from docutils.writers.html4css1 import Writer

    DOCUTILS_SETTINGS = {'output_encoding': 'utf-8',
                         'initial_header_level': 2}

    def render_rest(text):
        """Render the given ``text`` through the reStructuredText
        engine.

        FIXME: move to a unit test
        >>> render_rest('this is **bold**')
        u'<p>this is <strong>bold</strong></p>'
        """
        writer = Writer()
        parts = publish_parts(
            text, writer=writer, settings_overrides=DOCUTILS_SETTINGS)
        return parts['body'].strip()

    RENDERERS['rest'] = render_rest
