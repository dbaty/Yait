"""Test view utilities (``yait.views.utils``).

$Id$
"""

from unittest import TestCase


class TestTemplateAPI(TestCase):

    def setUp(self):
        from pyramid.configuration import Configurator
        self.config = Configurator()
        ## We need to register these templates since they are used in
        ## TemplateAPI.
        self.config.testing_add_template('templates/form_macros.pt')
        self.config.testing_add_template('templates/master.pt')
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _makeOne(self, request=None):
        from yait.views.utils import TemplateAPI
        if request is None:
            from pyramid.testing import DummyRequest
            request = DummyRequest()
        return TemplateAPI(request)

    def test_request_related_attributes(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            environ={'HTTP_REFERER': 'http://referrer.com'})
        api = self._makeOne(request=request)
        self.assert_(api.request is request)
        self.assert_(api.app_url, 'http://example.com')
        self.assert_(api.here_url, 'http://example.com')
        self.assert_(api.referrer, 'http://referrer.com')
        self.assert_(api.show_login_link)

    def test_status_message(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            params={'status_message': 'A status message.'},
            environ={'HTTP_REFERER': 'http://example.com/foo'})
        api = self._makeOne(request=request)
        self.assertEqual(api.status_message, 'A status message.')

    def test_error_message(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            params={'error_message': 'An error message.'},
            environ={'HTTP_REFERER': 'http://example.com/foo'})
        api = self._makeOne(request=request)
        self.assertEqual(api.error_message, 'An error message.')

    def test_status_message_foreign(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            params={'status_message': 'A status message.'},
            environ={'HTTP_REFERER': 'http://other.com'})
        api = self._makeOne(request=request)
        self.assertEqual(api.status_message, '')

    def test_error_message_foreign(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            params={'error_message': 'An error message.'},
            environ={'HTTP_REFERER': 'http://other.com'})
        api = self._makeOne(request=request)
        self.assertEqual(api.error_message, '')

    def test_no_login_link_in_login_form(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            url='http://exemple.com/login_form?came_from=foo')
        api = self._makeOne(request=request)
        self.assert_(not api.show_login_link)

    def test_user_related_anonymous(self):
        api = self._makeOne()
        self.assert_(not api.logged_in)
        self.assertEqual(api.user_cn, None)

    def test_user_related_logged_in(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            environ={'repoze.who.identity':
                         {'uid': u'john.smith',
                          'cn': u'John Smith'}})
        api = self._makeOne(request=request)
        self.assert_(api.logged_in)
        self.assertEqual(api.user_cn, u'John Smith')

    def test_user_related_no_cn(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest(
            environ={'repoze.who.identity':
                         {'uid': u'john.smith',
                          'cn': u''}})
        api = self._makeOne(request=request)
        self.assert_(api.logged_in)
        self.assertEqual(api.user_cn, u'john.smith')

    def test_misc_attributes(self):
        from pyramid.testing import DummyRequest        
        request = DummyRequest()
        api = self._makeOne(request=request)
        self.assertEqual(api.header_prefix, u'Yait')
        self.assertEqual(api.html_title_prefix, u'Yait')
        self.assert_(getattr(api.layout, 'render', None) is not None)
        self.assert_(getattr(api.form_macros, 'render', None) is not None)

    def test_url_of(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        request.application_url = 'http://exemple.com'
        api = self._makeOne(request=request)
        self.assertEqual(api.url_of(''), 'http://exemple.com')
        self.assertEqual(api.url_of('foo'), 'http://exemple.com/foo')
        self.assertEqual(api.url_of('foo/bar'), 'http://exemple.com/foo/bar')
        self.assertEqual(api.url_of('foo/bar/'), 'http://exemple.com/foo/bar')

    def test_has_permission(self):
        from pyramid.testing import DummyRequest
        def injected(request, *args):
            return request, args
        from yait.views import utils
        utils.has_permission = injected
        request = DummyRequest()
        api = self._makeOne(request=request)
        args = (1, 2, 3, 4)
        res = api.has_permission(*args)
        self.assertEqual(res, (request, args))


class TestGetUserMetadata(TestCase):

    def _callFUT(self, *args, **kwargs):
        from yait.views.utils import get_user_metadata
        return get_user_metadata(*args, **kwargs)

    def test_anonymous(self):
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(self._callFUT(request), None)

    def test_authenticated(self):
        from pyramid.testing import DummyRequest
        md = {'uid': u'john.smith', 'cn': u'John Smith'}
        request = DummyRequest(environ={'repoze.who.identity': md})
        self.assertEqual(self._callFUT(request), md)


class TestHasPermission(TestCase):

    def setUp(self):
        from yait.tests.base import get_testing_db_session
        self.session = get_testing_db_session()

    def tearDown(self):
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from yait.views.utils import has_permission
        return has_permission(*args, **kwargs)

    def _makeRequest(self, user_id=None):
        from pyramid.testing import DummyRequest
        environ = {}
        if user_id is not None:
            environ['repoze.who.identity'] = {'uid': user_id}
        return DummyRequest(environ=environ)

    def _makeProject(self, name=u'name', public=False):
        from yait.models import Project
        p = Project(name=name, title=u'title', public=public)
        self.session.add(p)
        self.session.flush() # need to flush to have an id
        return p

    def _makeSiteAdmin(self, user_id):
        from yait.models import Admin
        self.session.add(Admin(user_id=user_id))

    def _makeUser(self, user_id, roles=None):
        from yait.models import Role
        if roles is None:
            roles = {}
        for project, role in roles.items():
            r = Role(user_id=user_id, project_id=project.id, role=role)
            self.session.add(r)

    def test_unknown_permission(self):
        self.assertRaises(
            ValueError, self._callFUT,
            request=None, permission='Invalid permission')

    def test_invalid_permission_on_site(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        self.assertRaises(
            ValueError, self._callFUT,
            request=None, permission=PERM_ADMIN_PROJECT, context=None)

    def test_invalid_permission_on_project(self):
        from yait.views.utils import PERM_ADMIN_SITE
        project = self._makeProject()
        self.assertRaises(
            ValueError, self._callFUT,
            request=None, permission=PERM_ADMIN_SITE, context=project)

    def test_view_permission_on_public_project_for_anonymous(self):
        from yait.views.utils import PERM_VIEW_PROJECT
        request = self._makeRequest()
        project = self._makeProject(public=True)
        self.assert_(
            self._callFUT(request, PERM_VIEW_PROJECT, project))

    def test_non_view_permission_on_public_project_for_anonymous(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        request = self._makeRequest()
        project = self._makeProject(public=True)
        self.assert_(
            not self._callFUT(request, PERM_ADMIN_PROJECT, project))

    def test_view_permission_on_private_project_for_anonymous(self):
        from yait.views.utils import PERM_VIEW_PROJECT
        request = self._makeRequest()
        project = self._makeProject()
        self.assert_(
            not self._callFUT(request, PERM_VIEW_PROJECT, project))

    def test_site_permission_for_site_admin(self):
        from yait.views.utils import PERM_ADMIN_SITE
        request = self._makeRequest(user_id=u'site_admin')
        self._makeSiteAdmin(u'site_admin')
        self.assert_(
            self._callFUT(request, PERM_ADMIN_SITE))

    def _test_role(self, user_id, project, expected):
        ## An helper method for all 'test_role_*()' below
        from yait.views.utils import PERM_VIEW_PROJECT
        from yait.views.utils import PERM_PARTICIPATE_IN_PROJECT
        from yait.views.utils import PERM_SEE_PRIVATE_TIMING_INFO
        from yait.views.utils import PERM_ADMIN_PROJECT
        missing_perms = set(
            ['view', 'participate', 'see_timing', 'admin_project']
            ).difference(expected.keys())
        assert not missing_perms, \
            'The following permissions are not tested: %s' % missing_perms
        request = self._makeRequest(user_id=user_id)
        for key, permission in {
            'view': PERM_VIEW_PROJECT,
            'participate': PERM_PARTICIPATE_IN_PROJECT,
            'see_timing': PERM_SEE_PRIVATE_TIMING_INFO,
            'admin_project': PERM_ADMIN_PROJECT}.items():
            allowed = expected[key]
            self.assertEqual(
                self._callFUT(request, permission, project), allowed)

    def test_role_site_admin(self):
        project = self._makeProject()
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        self._test_role(user_id, project, {
                'view': True,
                'participate': True,
                'see_timing': True,
                'admin_project': True})

    def test_role_project_admin(self):
        from yait.views.utils import ROLE_PROJECT_ADMIN
        project = self._makeProject()
        user_id = u'project_admin'
        self._makeUser(user_id, roles={project: ROLE_PROJECT_ADMIN})
        self._test_role(user_id, project, {
                'view': True,
                'participate': True,
                'see_timing': True,
                'admin_project': True})

    def test_role_project_internal_participant(self):
        from yait.views.utils import ROLE_PROJECT_INTERNAL_PARTICIPANT
        project = self._makeProject()
        user_id = u'internal_participant'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_INTERNAL_PARTICIPANT})
        self._test_role(user_id, project, {
                'view': True,
                'participate': True,
                'see_timing': True,
                'admin_project': False})

    def test_role_project_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        project = self._makeProject()
        user_id = u'participant'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_PARTICIPANT})
        self._test_role(user_id, project, {
                'view': True,
                'participate': True,
                'see_timing': False,
                'admin_project': False})

    def test_role_project_viewer(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        project = self._makeProject()
        user_id = u'project_viewer'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_VIEWER})
        self._test_role(user_id, project, {
                'view': True,
                'participate': False,
                'see_timing': False,
                'admin_project': False})

    def test_no_role(self):
        project = self._makeProject()
        user_id = u'no_role'
        self._makeUser(user_id)
        self._test_role(user_id, project, {
                'view': False,
                'participate': False,
                'see_timing': False,
                'admin_project': False})

    def test_role_in_another_project(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        project1 = self._makeProject(name=u'p1')
        project2 = self._makeProject(name=u'p2')
        user_id = u'user1'
        ## give role in project 1
        self._makeUser(user_id, roles={project1: PERM_ADMIN_PROJECT})
        ## but check in project 2
        self._test_role(user_id, project2, {
                'view': False,
                'participate': False,
                'see_timing': False,
                'admin_project': False})

    def test_cache_site_permissions(self):
        from yait.models import Admin
        from yait.views.utils import PERM_ADMIN_SITE
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        request = self._makeRequest(user_id=user_id)
        self.assert_(self._callFUT(request, PERM_ADMIN_SITE))
        role = self.session.query(Admin).one()
        self.session.delete(role)
        self.assert_(self._callFUT(request, PERM_ADMIN_SITE, None))

    def test_cache_project_permissions(self):
        from yait.models import Role
        from yait.views.utils import PERM_ADMIN_PROJECT
        from yait.views.utils import ROLE_PROJECT_ADMIN
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id, roles={project: ROLE_PROJECT_ADMIN})
        request = self._makeRequest(user_id=user_id)
        self.assert_(self._callFUT(request, PERM_ADMIN_PROJECT, project))
        role = self.session.query(Role).one()
        self.session.delete(role)
        self.assert_(self._callFUT(request, PERM_ADMIN_PROJECT, project))


class TestRollbackTransaction(TestCase):

    def _callFUT(self, environ, status=None):
        from yait.views.utils import rollback_transaction
        return rollback_transaction(environ, status, None)

    def test_rollback_on_get(self):
        environ = {'REQUEST_METHOD': 'GET'}
        self.assertEqual(self._callFUT(environ), True)

    def test_rollback_when_4xx(self):
        environ = {'REQUEST_METHOD': 'POST'}
        self.assertEqual(self._callFUT(environ, '400'), True)

    def test_rollback_when_5xx(self):
        environ = {'REQUEST_METHOD': 'POST'}
        self.assertEqual(self._callFUT(environ, '500'), True)

    def test_commit_when_2xx(self):
        environ = {'REQUEST_METHOD': 'POST'}
        self.assertEqual(self._callFUT(environ, '200'), False)
