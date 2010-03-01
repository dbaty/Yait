"""Views available through AJAX.

$Id$
"""

from yait.utils import renderReST


def ajax_renderReST(context, request):
    """Render reStructuredText (called via AJAX)."""
    text = request.params.get('text', '')
    return dict(rendered=renderReST(text))
