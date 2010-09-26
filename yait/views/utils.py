"""View utilities.

$Id$
"""

from repoze.bfg.renderers import get_renderer

from sqlalchemy.orm.exc import NoResultFound

from yait.models import Admin
from yait.models import DBSession
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
                         PERM_SEE_PRIVATE_TIMING_INFO,
                         PERM_PARTICIPATE_IN_PROJECT,
                         PERM_VIEW_PROJECT),
    ROLE_PROJECT_INTERNAL_PARTICIPANT: (PERM_SEE_PRIVATE_TIMING_INFO,
                                        PERM_PARTICIPATE_IN_PROJECT,
                                        PERM_VIEW_PROJECT),
    ROLE_PROJECT_PARTICIPANT: (PERM_PARTICIPATE_IN_PROJECT,
                               PERM_VIEW_PROJECT),
    ROLE_PROJECT_VIEWER: (PERM_VIEW_PROJECT, )}


class TemplateAPI(object):
    """Provides a master template and various information and
    utilities that can be used in any template.
    """
    def __init__(self, context, request):
        self.request = request
        self.app_url = request.application_url
        self.here_url = request.url
        self.referrer = request.environ.get('HTTP_REFERER', '')
        self.header_prefix = HEADER_PREFIX
        self.html_title_prefix = HTML_TITLE_PREFIX
        if self.referrer.startswith(request.application_url):
            self.status_message = request.params.get('status_message', '')
            self.error_message = request.params.get('error_message', '')
        else:
            self.status_message = self.error_message = ''
        self.layout = get_renderer(
            'templates/master.pt').implementation()
        self.form_macros = get_renderer(
            'templates/form_macros.pt').implementation().macros
        self.show_login_link = True
        if self.here_url.split('?')[0].endswith('login_form'):
            self.show_login_link = False
        md = get_user_metadata(request)
        self.logged_in = md is not None
        self.user_cn = None
        if self.logged_in:
            self.user_cn = md.get('cn') or md.get('uid')

    def url_of(self, path):
        return '/'.join((self.app_url, path)).strip('/')

    def has_permission(self, *args, **kwargs):
        return has_permission(self.request, *args, **kwargs)


def get_user_metadata(request):
    return request.environ.get('repoze.who.identity', None)


def has_permission(request, permission, context=None):
    """Return whether the current user is granted the given
    ``permission`` in this ``context``.

    Context must be a ``Project`` on which the permission is to be
    checked, or ``None`` if the permission is to be checked on the
    root level. In the latter case, only ``PERM_ADMIN_SITE`` may be
    checked (because other permissions do not make sense outside of
    projects).
    """
    if permission not in ALL_PERMS:
        raise ValueError(u'Unknown permission: "%s"' % permission)
    if not context and permission != PERM_ADMIN_SITE:
        raise ValueError(
            u'Wrong permission on a site: "%s"' % permission)
    if context and permission == PERM_ADMIN_SITE:
        raise ValueError(
            u'Wrong permission on a project: "%s"' % permission)

    cache_key_admin = '_user_is_site_admin'
    if getattr(request, cache_key_admin, None):
        return True

    if context is None:
        cache_key = '_user_site_perms'
    else:
        cache_key = '_user_perms_%s' % context.name
    if getattr(request, cache_key, None) is not None:
        return permission in getattr(request, cache_key)

    ## Shortcuts for public projects and anonymous users
    if context is not None and context.public and \
            permission == PERM_VIEW_PROJECT:
        return True
    user_id = (get_user_metadata(request) or {}).get('uid', None)
    if not user_id:
        return False

    session = DBSession()
    user_perms = ()
    if session.query(Admin).filter_by(user_id=user_id).first():
        user_perms = PERMISSIONS_FOR_ROLE[ROLE_SITE_ADMIN]
        setattr(request, cache_key_admin, True)
    elif context is not None:
        try:
            row = session.query(Role).filter_by(
                user_id=user_id, project_id=context.id).one()
        except NoResultFound:
            pass
        else:
            user_perms = PERMISSIONS_FOR_ROLE[row.role]

    setattr(request, cache_key, user_perms)
    return permission in user_perms


def rollback_transaction(environ, status, headers):
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
