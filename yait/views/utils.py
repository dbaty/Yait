"""View utilities.

$Id$
"""

from repoze.bfg.chameleon_zpt import get_template

from yait.models import _getStore
from yait.models import Manager
from yait.models import Role


## Template constants
HEADER_PREFIX = u'Yait'
HTML_TITLE_PREFIX = HEADER_PREFIX

## Permissions and roles
PERM_ADMIN_SITE = u'Administer site'
PERM_ADMIN_PROJECT = u'Administer project'
PERM_VIEW_PROJECT = u'View project'
PERM_PARTICIPATE_IN_PROJECT = u'Participate in project'
PERM_SEE_PRIVATE_TIMING_INFO = u'See private time information'
ALL_PERMS = (PERM_ADMIN_SITE, PERM_ADMIN_PROJECT, PERM_VIEW_PROJECT,
             PERM_PARTICIPATE_IN_PROJECT, PERM_SEE_PRIVATE_TIMING_INFO)
ROLE_SITE_ADMIN = u'Site administrator'
ROLE_PROJECT_ADMIN = 1
ROLE_PROJECT_VIEWER = 2
ROLE_PROJECT_PARTICIPANT = 3
ROLE_PROJECT_INTERNAL_PARTICIPANT = 4
PERMISSIONS_FOR_ROLE = {
    ROLE_SITE_ADMIN: ALL_PERMS,
    ROLE_PROJECT_ADMIN: (PERM_ADMIN_PROJECT,
                         PERM_VIEW_PROJECT, PERM_PARTICIPATE_IN_PROJECT,
                         PERM_SEE_PRIVATE_TIMING_INFO),
    ROLE_PROJECT_VIEWER: (PERM_VIEW_PROJECT, ),
    ROLE_PROJECT_PARTICIPANT: (PERM_VIEW_PROJECT,
                               PERM_PARTICIPATE_IN_PROJECT),
    ROLE_PROJECT_PARTICIPANT: (PERM_VIEW_PROJECT,
                               PERM_PARTICIPATE_IN_PROJECT,
                               PERM_SEE_PRIVATE_TIMING_INFO)}


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
        referrer = request.headers.get('Referer', '')
        if referrer.startswith(request.application_url):
            self.status_message = request.params.get('status_message', '')
            self.error_message = request.params.get('error_message', '')
        else:
            self.status_message = self.error_message = ''
        self.layout = get_template('templates/master.pt')
        self.form_macros = get_template('templates/form_macros.pt').macros
        self.show_login_link = True
        if self.here_url.split('?')[0].endswith('login_form'):
            self.show_login_link = False
        self.user_cn = getUserMetadata(request).get('cn', None)

    def urlOf(self, path):
        return '/'.join((self.app_url, path)).strip('/')

    def hasPermission(self, *args, **kwargs):
        return hasPermission(self.request, *args, **kwargs)


def getUserMetadata(request):
    return request.environ.get('repoze.who.identity', {})


def isLoggedIn(request):
    return request.environ.get('repoze.who.identity') is not None


def hasPermission(request, permission, context=None):
    """Return whether the current user is granted the given
    ``permission`` in this ``context``.

    Context must be a ``Project`` on which the permission is to be
    checked, or ``None`` if the permission is to be checked on the
    root level. In the latter case, only ``PERM_ADMIN_SITE`` may be
    checked (because other permissions do not make sense outside of
    projects).
    """
    assert permission in ALL_PERMS, 'Unknown permission: %s' % permission
    assert context or (permission == PERM_ADMIN_SITE)

    cache_key_admin = '_user_is_site_admin'
    if getattr(request, cache_key_admin, None):
        return True

    if context is None:
        cache_key = '_user_site_perms' ## will never be read, actually
    else:
        cache_key = '_user_perms_%s' % context.name
    if getattr(request, cache_key, None) is not None:
        return permission in getattr(request, cache_key)

    ## Shortcuts for public projects and anonymous users
    if context is not None and context.is_public and \
            permission == PERM_VIEW_PROJECT:
        return True
    if not isLoggedIn(request):
        return False

    ## FIXME: we should also look for permissions granted to the
    ## groups the user belongs to.
    user_id = getUserMetadata(request)['uid']
    user_id = unicode(user_id) ## FIXME: is this not a work around another problem?
    store = _getStore()

    if store.find(Manager, user_id=user_id):
        user_perms = PERMISSIONS_FOR_ROLE[ROLE_SITE_ADMIN]
        setattr(request, cache_key_admin, True)
    else:
        row = store.find(Role, user_id=user_id).one()
        if row is not None:
            user_perms = PERMISSIONS_FOR_ROLE[Role.role]
        else:
            user_perms = ()

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
