"""Authentication and authorization policies, roles and permissions.

Views are defined in the 'yait.views.auth' module, not here.
"""

from pyramid.security import authenticated_userid

from sqlalchemy.orm.exc import NoResultFound

from yait.models import DBSession
from yait.models import Role
from yait.models import User


PERM_ADMIN_SITE = u'Administer site'
PERM_MANAGE_PROJECT = u'Manage project'
PERM_VIEW_PROJECT = u'View project'
PERM_PARTICIPATE_IN_PROJECT = u'Participate in project'
PERM_SEE_PRIVATE_TIMING_INFO = u'See private time information'
ALL_PERMS = (PERM_ADMIN_SITE, PERM_MANAGE_PROJECT, PERM_VIEW_PROJECT,
             PERM_PARTICIPATE_IN_PROJECT, PERM_SEE_PRIVATE_TIMING_INFO)
ROLE_SITE_ADMIN = u'Site administrator'
ROLE_PROJECT_MANAGER = 1
ROLE_PROJECT_VIEWER = 2
ROLE_PROJECT_PARTICIPANT = 3
ROLE_PROJECT_INTERNAL_PARTICIPANT = 4
PERMISSIONS_FOR_ROLE = {
    ROLE_SITE_ADMIN: ALL_PERMS,
    ROLE_PROJECT_MANAGER: (PERM_MANAGE_PROJECT,
                           PERM_SEE_PRIVATE_TIMING_INFO,
                           PERM_PARTICIPATE_IN_PROJECT,
                           PERM_VIEW_PROJECT),
    ROLE_PROJECT_INTERNAL_PARTICIPANT: (PERM_SEE_PRIVATE_TIMING_INFO,
                                        PERM_PARTICIPATE_IN_PROJECT,
                                        PERM_VIEW_PROJECT),
    ROLE_PROJECT_PARTICIPANT: (PERM_PARTICIPATE_IN_PROJECT,
                               PERM_VIEW_PROJECT),
    ROLE_PROJECT_VIEWER: (PERM_VIEW_PROJECT, )}
ROLE_LABELS = {ROLE_PROJECT_MANAGER: u'Project manager',
               ROLE_PROJECT_VIEWER: u'Viewer',
               ROLE_PROJECT_PARTICIPANT: u'Participant',
               ROLE_PROJECT_INTERNAL_PARTICIPANT: u'Internal participant'}

class _AnonymousUser(object):
    def __init__(self):
        self.id = None
        self.is_admin = False


def _get_user(request):
    """Return an instance of the ``User`` class if the user is logged
    in, or ``AnonymousUser`` otherwise.

    This function is never called explicitely by our code: it
    corresponds to the ``user`` reified property on requests (see
    ``app`` module where we call ``set_request_property()``).
    """
    user = None
    user_id = authenticated_userid(request)
    if user_id:
        session = DBSession()
        try:
            user = session.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            user = None
    if user is None:
        return _AnonymousUser()
    return user


def check_password(login, password):
    """Return the corresponding user if the given credentials are
    correct.
    """
    session = DBSession()
    try:
        user = session.query(User).filter_by(login=login).one()
    except NoResultFound:
        return None
    if not user.validate_password(password):
        return None
    return user


class AuthorizationPolicy(object):
    pass  # FIXME


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
