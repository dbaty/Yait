"""Authentication and authorization policies.

Views are defined in the 'yait.views.auth' module, not here.
"""

from pyramid.security import authenticated_userid

from sqlalchemy.orm.exc import NoResultFound

from yait.models import DBSession
from yait.models import User


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
    """Return whether the credentials match one of our user's."""
    session = DBSession()
    try:
        user = session.query(User).filter_by(login=login).one()
    except NoResultFound:
        return False
    return user.validate_password(password)


class AuthorizationPolicy(object):
    pass  # FIXME
