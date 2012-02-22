"""Base utilities and classes for our tests."""


from unittest import TestCase

from pyramid import testing
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.decorator import reify


def get_testing_db_session():
    from yait.models import DBSession
    from yait.models import initialize_sql
    initialize_sql('sqlite://')
    return DBSession


class DummyAuthenticationPolicy(CallbackAuthenticationPolicy):
    def __init__(self, *args, **kwargs):
        pass

    # Handy method used by our tests, not by the application itself.
    @staticmethod
    def fake_login(request, user_id):
        request._dummy_auth_id = user_id

    def unauthenticated_userid(self, request):
        return getattr(request, '_dummy_auth_id', None)


# A simplified version of 'pyramid.util.InstancePropertyMixin.set_property'
def _set_property(request, name, callable, do_reify=False):
    func = lambda this: callable(this)
    func.__name__ = name
    if do_reify:
        func = reify(func)
    attrs = {name: func}
    parent = request.__class__
    cls = type(parent.__name__, (parent, object), attrs)
    request.__class__ = cls


class TestCaseForViews(TestCase):

    def setUp(self):
        from yait.app import _set_auth_policies
        self.config = testing.setUp()
        # FIXME: check that it is still true
        # We need to register these templates since they are used in
        # TemplateAPI which is in turn used in almost all views.
        self.config.testing_add_template('templates/form_macros.pt')
        self.config.testing_add_template('templates/master.pt')
        _set_auth_policies(self.config, {'yait.auth.timeout': '10',
                                         'yait.auth.secret': 'secret',
                                         'yait.auth.secure_only': 'false'},
                           DummyAuthenticationPolicy)
        self.session = get_testing_db_session()

    def tearDown(self):
        testing.tearDown()
        self.session.remove()

    def _make_renderer(self):
        return self.config.testing_add_renderer(self.template_under_test)

    def _make_request(self, user=None, post=None, get=None, matchdict=None):
        from pyramid.testing import DummyRequest
        from yait.auth import _get_user
        from yait.models import User
        if post is not None:
            from webob.multidict import MultiDict
            post = MultiDict(post)
        request = DummyRequest(params=get, post=post)
        _set_property(request, 'user', _get_user, do_reify=True)
        if user:
            # 'user' may be the user id or the login.
            if isinstance(user, unicode):
                user = self.session.query(User).filter_by(login=user).one().id
            DummyAuthenticationPolicy.fake_login(request, user)
        if matchdict is not None:
            request.matchdict = matchdict
        return request

    def _make_user(self, login, fullname=u'', is_admin=False, roles=None):
        from yait.models import Role
        from yait.models import User
        if roles is None:
            roles = {}
        user = User(login=login, password=u'secret', fullname=fullname,
                    email=u'', is_admin=is_admin)
        self.session.add(user)
        self.session.flush()  # sets id
        for project, role in roles.items():
            r = Role(user_id=user.id, project_id=project.id, role=role)
            self.session.add(r)
        return user

    def _make_project(self, name=u'name', title=u'title', public=False):
        from yait.models import Project
        p = Project(name=name, title=title, public=public)
        self.session.add(p)
        self.session.flush()  # sets id
        return p

    def _make_issue(self, project, ref=1,
                    title=u'Title', reporter=u'reporter', assignee=u'assignee',
                    kind=None, priority=None, status=None,
                    resolution=None, deadline=None,
                    time_estimated=0, time_billed=0):
        from yait.models import Issue
        from yait.models import DEFAULT_ISSUE_KIND
        from yait.models import DEFAULT_ISSUE_PRIORITY
        from yait.models import DEFAULT_ISSUE_STATUS
        if kind is None:
            kind = DEFAULT_ISSUE_KIND
        if priority is None:
            priority = DEFAULT_ISSUE_PRIORITY
        if status is None:
            status = DEFAULT_ISSUE_STATUS
        i = Issue(project_id=project.id,
                  ref=ref,
                  title=title,
                  reporter=reporter,
                  kind=kind,
                  priority=priority,
                  status=status,
                  resolution=resolution,
                  deadline=deadline,
                  time_estimated=time_estimated,
                  time_billed=time_billed)
        self.session.add(i)
        self.session.flush()  # need to flush to have an id later
        return i
