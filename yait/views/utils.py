"""View utilities."""

from pyramid.renderers import get_renderer

from sqlalchemy.orm.exc import NoResultFound

from yait.models import DBSession
from yait.models import Role


# Template constants
HEADER_PREFIX = u'Yait'
HTML_TITLE_PREFIX = HEADER_PREFIX

# Permissions and roles
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
    """Provide a master template and various information and utilities
    that can be used in any template.
    """
    def __init__(self, request):
        self.request = request
        # FIXME: fix these titles. The HTML title prefix should be
        # 'Yait - %(title)s' where title is given as a parameter to
        # the constructor.
        # As for the 'header_prefix', that should just be 'Yait'.
        self.header_prefix = HEADER_PREFIX
        self.html_title_prefix = HTML_TITLE_PREFIX
        self.notifications = {
            'success': self.request.session.pop_flash('success'),
            'error': self.request.session.pop_flash('error')}
        self.layout = get_renderer('../templates/layout.pt').implementation()
        self.form_macros = get_renderer(
            '../templates/form_macros.pt').implementation().macros
        self.logged_in = request.user.id is not None
        self.show_login_link = not self.logged_in
        self.is_admin = request.user.is_admin

    def route_url(self, route_name, *elements, **kw):
        return self.request.route_url(route_name, *elements, **kw)

    def static_url(self, path, **kw):
        if ':' not in path:
            path = 'yait:%s' % path
        return self.request.static_url(path, **kw)

    # FIXME: not sure this is a good idea to provide this shortcut. We
    # should probably not call 'has_permission()' from the templates.
    def has_permission(self, *args, **kwargs):
        return has_permission(self.request, *args, **kwargs)


# FIXME: this should probably be moved to the 'auth' module
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

    # Shortcuts for public projects and anonymous users
    if context is not None and context.public and \
            permission == PERM_VIEW_PROJECT:
        return True
    user_id = request.user.id
    if not user_id:
        return False

    session = DBSession()
    user_perms = ()
    if request.user.is_admin:
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
