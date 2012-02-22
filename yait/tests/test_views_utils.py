"""Test view utilities (``yait.views.utils``)."""

from unittest import TestCase

from pyramid import testing

from yait.tests.base import TestCaseForViews


# FIXME: to be reviewed when the class is cleaned up.
# class TestTemplateAPI(TestCaseForViews):

#     def setUp(self):
#         self.config = testing.setUp()
#         # We need to register these templates since they are used in
#         # TemplateAPI.
#         self.config.testing_add_template('../templates/form_macros.pt')
#         self.config.testing_add_template('../templates/master.pt')
#         self.config.begin()

#     def tearDown(self):
#         testing.tearDown()

#     def _make_one(self, request=None):
#         from yait.views.utils import TemplateAPI
#         if request is None:
#             request = self._make_request()
#         return TemplateAPI(request)

#     def test_request_related_attributes(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             environ={'HTTP_REFERER': 'http://referrer.com'})
#         api = self._make_one(request=request)
#         self.assert_(api.request is request)
#         self.assert_(api.app_url, 'http://example.com')
#         self.assert_(api.here_url, 'http://example.com')
#         self.assert_(api.referrer, 'http://referrer.com')
#         self.assert_(api.show_login_link)

#     def test_status_message(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             params={'status_message': 'A status message.'},
#             environ={'HTTP_REFERER': 'http://example.com/foo'})
#         api = self._make_one(request=request)
#         self.assertEqual(api.status_message, 'A status message.')

#     def test_error_message(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             params={'error_message': 'An error message.'},
#             environ={'HTTP_REFERER': 'http://example.com/foo'})
#         api = self._make_one(request=request)
#         self.assertEqual(api.error_message, 'An error message.')

#     def test_status_message_foreign(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             params={'status_message': 'A status message.'},
#             environ={'HTTP_REFERER': 'http://other.com'})
#         api = self._make_one(request=request)
#         self.assertEqual(api.status_message, '')

#     def test_error_message_foreign(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             params={'error_message': 'An error message.'},
#             environ={'HTTP_REFERER': 'http://other.com'})
#         api = self._make_one(request=request)
#         self.assertEqual(api.error_message, '')

#     def test_no_login_link_in_login_form(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             url='http://exemple.com/login_form?next=foo')
#         api = self._make_one(request=request)
#         self.assert_(not api.show_login_link)

#     def test_user_related_anonymous(self):
#         api = self._make_one()
#         self.assert_(not api.logged_in)
#         self.assertEqual(api.user_cn, None)

#     def test_user_related_logged_in(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             environ={'repoze.who.identity':
#                          {'uid': u'john.smith',
#                           'cn': u'John Smith'}})
#         api = self._make_one(request=request)
#         self.assert_(api.logged_in)
#         self.assertEqual(api.user_cn, u'John Smith')

#     def test_user_related_no_cn(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest(
#             environ={'repoze.who.identity':
#                          {'uid': u'john.smith',
#                           'cn': u''}})
#         api = self._make_one(request=request)
#         self.assert_(api.logged_in)
#         self.assertEqual(api.user_cn, u'john.smith')

#     def test_misc_attributes(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest()
#         api = self._make_one(request=request)
#         self.assertEqual(api.header_prefix, u'Yait')
#         self.assertEqual(api.html_title_prefix, u'Yait')
#         self.assert_(getattr(api.layout, 'render', None) is not None)
#         self.assert_(getattr(api.form_macros, 'render', None) is not None)

#     def test_url_of(self):
#         from pyramid.testing import DummyRequest
#         request = DummyRequest()
#         request.application_url = 'http://baz.com'
#         api = self._make_one(request=request)
#         self.assertEqual(api.url_of(''), 'http://baz.com')
#         self.assertEqual(api.url_of('foo'), 'http://baz.com/foo')
#         self.assertEqual(api.url_of('foo/bar'), 'http://baz.com/foo/bar')
#         self.assertEqual(api.url_of('foo/bar/'), 'http://baz.com/foo/bar')

#     def test_has_permission(self):
#         from pyramid.testing import DummyRequest
#         def injected(request, *args):
#             return request, args
#         from yait.views import utils
#         utils.has_permission = injected
#         request = DummyRequest()
#         api = self._make_one(request=request)
#         args = (1, 2, 3, 4)
#         res = api.has_permission(*args)
#         self.assertEqual(res, (request, args))


class TestHasPermission(TestCaseForViews):

    def _call_fut(self, *args, **kwargs):
        from yait.views.utils import has_permission
        return has_permission(*args, **kwargs)

    def test_unknown_permission(self):
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission='Invalid permission')

    def test_invalid_permission_on_site(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission=PERM_ADMIN_PROJECT, context=None)

    def test_invalid_permission_on_project(self):
        from yait.views.utils import PERM_ADMIN_SITE
        project = self._make_project()
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission=PERM_ADMIN_SITE, context=project)

    def test_view_permission_on_public_project_for_anonymous(self):
        from yait.views.utils import PERM_VIEW_PROJECT
        request = self._make_request()
        project = self._make_project(public=True)
        self.assert_(self._call_fut(request, PERM_VIEW_PROJECT, project))

    def test_non_view_permission_on_public_project_for_anonymous(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        request = self._make_request()
        project = self._make_project(public=True)
        self.assert_(not self._call_fut(request, PERM_ADMIN_PROJECT, project))

    def test_view_permission_on_private_project_for_anonymous(self):
        from yait.views.utils import PERM_VIEW_PROJECT
        request = self._make_request()
        project = self._make_project()
        self.assert_(not self._call_fut(request, PERM_VIEW_PROJECT, project))

    def test_site_permission_for_site_admin(self):
        from yait.views.utils import PERM_ADMIN_SITE
        login = u'admin'
        self._make_user(login, is_admin=True)
        request = self._make_request(user=login)
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))

    def _test_role(self, login, project, expected):
        # An helper method for all 'test_role_*()' below
        from yait.views.utils import PERM_VIEW_PROJECT
        from yait.views.utils import PERM_PARTICIPATE_IN_PROJECT
        from yait.views.utils import PERM_SEE_PRIVATE_TIMING_INFO
        from yait.views.utils import PERM_ADMIN_PROJECT
        missing_perms = set(
            ['view', 'participate', 'see_timing', 'admin_project']
            ).difference(expected.keys())
        assert not missing_perms, \
            'The following permissions are not tested: %s' % missing_perms
        request = self._make_request(user=login)
        for key, permission in {
            'view': PERM_VIEW_PROJECT,
            'participate': PERM_PARTICIPATE_IN_PROJECT,
            'see_timing': PERM_SEE_PRIVATE_TIMING_INFO,
            'admin_project': PERM_ADMIN_PROJECT}.items():
            allowed = expected[key]
            self.assertEqual(
                self._call_fut(request, permission, project), allowed)

    def test_role_site_admin(self):
        project = self._make_project()
        login = u'admin'
        self._make_user(login, is_admin=True)
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'admin_project': True}
        self._test_role(login, project, expected)

    def test_role_project_admin(self):
        from yait.views.utils import ROLE_PROJECT_ADMIN
        project = self._make_project()
        login = u'project_admin'
        self._make_user(login, roles={project: ROLE_PROJECT_ADMIN})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'admin_project': True}
        self._test_role(login, project, expected)

    def test_role_project_internal_participant(self):
        from yait.views.utils import ROLE_PROJECT_INTERNAL_PARTICIPANT
        project = self._make_project()
        login = u'internal_participant'
        self._make_user(login, roles={
                project: ROLE_PROJECT_INTERNAL_PARTICIPANT})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'admin_project': False}
        self._test_role(login, project, expected)

    def test_role_project_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        project = self._make_project()
        login = u'participant'
        self._make_user(login, roles={project: ROLE_PROJECT_PARTICIPANT})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': False,
                    'admin_project': False}
        self._test_role(login, project, expected)

    def test_role_project_viewer(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        project = self._make_project()
        login = u'project_viewer'
        self._make_user(login, roles={project: ROLE_PROJECT_VIEWER})
        expected = {'view': True,
                    'participate': False,
                    'see_timing': False,
                    'admin_project': False}
        self._test_role(login, project, expected)

    def test_no_role(self):
        project = self._make_project()
        login = u'no_role'
        self._make_user(login)
        expected = {'view': False,
                    'participate': False,
                    'see_timing': False,
                    'admin_project': False}
        self._test_role(login, project, expected)

    def test_role_in_another_project(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        project1 = self._make_project(name=u'p1')
        project2 = self._make_project(name=u'p2')
        login = u'user1'
        # give role in project 1
        self._make_user(login, roles={project1: PERM_ADMIN_PROJECT})
        # but check in project 2
        expected = {'view': False,
                    'participate': False,
                    'see_timing': False,
                    'admin_project': False}
        self._test_role(login, project2, expected)

    def test_cache_site_permissions(self):
        from yait.views.utils import PERM_ADMIN_SITE
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        request = self._make_request(login)
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))
        admin.is_admin = False
        self.session.flush()
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))

    def test_cache_project_permissions(self):
        from yait.models import Role
        from yait.views.utils import PERM_ADMIN_PROJECT
        from yait.views.utils import ROLE_PROJECT_ADMIN
        project = self._make_project()
        login = u'user1'
        self._make_user(login, roles={project: ROLE_PROJECT_ADMIN})
        request = self._make_request(user=login)
        self.assert_(self._call_fut(request, PERM_ADMIN_PROJECT, project))
        role = self.session.query(Role).one()
        self.session.delete(role)
        self.assert_(self._call_fut(request, PERM_ADMIN_PROJECT, project))
