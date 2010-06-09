"""View utilities.

$Id$
"""

from repoze.bfg.chameleon_zpt import get_template

from storm.exceptions import NotOneError

from yait.models import _getStore
from yait.models import Manager
from yait.models import Permission


## Template constants
HEADER_PREFIX = u'Yait'
HTML_TITLE_PREFIX = HEADER_PREFIX

## Permissions
PERM_ADMIN_YAIT = 'Administer Yait'
PERM_ADMIN_PROJECT = 'Administer project'
PERM_VIEW_PROJECT = 'View project'
PERM_PARTICIPATE_IN_PROJECT = 'Participate in project'
PERM_SEE_PRIVATE_TIMING_INFO = 'See private timing information'
PERM_VALUES = {PERM_ADMIN_YAIT: 1,
               PERM_ADMIN_PROJECT: 2,
               PERM_VIEW_PROJECT: 4,
               PERM_PARTICIPATE_IN_PROJECT: 8,
               PERM_SEE_PRIVATE_TIMING_INFO: 16}


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
        self.show_login_link = True
        if self.here_url.split('?')[0].endswith('login_form'):
            self.show_login_link = False
        self.user_cn = getUserMetadata(request).get('cn', None)

    def urlOf(self, path):
        return '/'.join((self.app_url, path)).strip('/')


def getUserMetadata(request):
    return request.environ.get('repoze.who.identity', {})


def isLoggedIn(request):
    return request.environ.get('repoze.who.identity') is not None


def hasPermission(request, permission, context=None):
    """Return whether the current user is granted the given
    ``permission`` in this ``context``.

    Context must be a ``Project`` on which the permission is to be
    checked, or ``None`` if the permission is to be checked on the
    root level. In the latter case, only ``PERM_ADMIN_YAIT`` may be
    checked (because other permissions do not make sense outside of
    projects).
    """
    assert context or (permission == PERM_ADMIN_YAIT)

    if context is None:
        cache_key = '_user_perms_global'
    else:
        cache_key = '_user_perms_%s' % context.name
    if getattr(request, cache_key, None) is not None:
        return permission in getattr(request, cache_key)

    ## Shortcut for public projects
    if context is not None and context.is_public and \
            permission == PERM_VIEW_PROJECT:
        return True

    if not isLoggedIn(request):
        return False

    ## FIXME: we should also look for permissions granted to the
    ## groups the use belongs to.
    user_id = getUserMetadata(request)['uid']
    user_id = unicode(user_id) ## FIXME: is this not a work around another problem?
    store = _getStore()
    user_perm_values = 0
    if store.find(Manager, user_id=user_id):
        user_perm_values = PERM_VALUES[PERM_ADMIN_YAIT]
    if context is not None:
        row = store.find(Permission, user_id=user_id).one()
        if row is not None:
            user_perm_values ^= row.perms

    ## Turn integer value into a list of permissions
    user_perms = []
    for perm, value in PERM_VALUES.items():
        if user_perm_values & value:
            user_perms.append(perm)
    setattr(request, cache_key, user_perms)
    return permission in user_perms


def commit_veto(environ, status, headers):
    """Returns whether the transaction machinery should cancel the
    transaction.

    This hook is called by ``repoze.tm2`` to know whether it should
    roll back or commit the db transaction: if this methods returns
    ``True``, the transaction is cancelled; otherwise, it is
    committed.
    """
    if environ['REQUEST_METHOD'] == 'GET':
        return True
    return status.startswith('4') or status.startswith('5')
