"""View utilities.

$Id$
"""

from repoze.bfg.chameleon_zpt import get_template


HEADER_PREFIX = u'Yait'
HTML_TITLE_PREFIX = HEADER_PREFIX

class TemplateAPI(object):
    """Provides a master template and various information and
    utilities that can be used in any template.
    """
    def __init__(self, context, request):
        self.request = request
        self.app_url = request.application_url
        self.here_url = request.url
        self.referrer = request.environ.get('HTTP_REFERER', None)
        self.header_prefix = HEADER_PREFIX
        self.html_title_prefix = HTML_TITLE_PREFIX
        self.layout = get_template('templates/master.pt')

    def urlOf(self, path):
        return '/'.join((self.app_url, path)).strip('/')


def commit_veto(environ, status, headers):
    """Hook called by repoze.tm2 to know whether it should commit the
    db transaction.
    """
    if environ['REQUEST_METHOD'] == 'GET':
        return True
    return status.startswith('4') or status.startswith('5')
