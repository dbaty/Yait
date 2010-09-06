"""Test view utilities (``yait.views.utils``).

$Id$
"""

from unittest import TestCase


class TestTemplateAPI(TestCase):

    def setUp(self):
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        ## We need to register these templates since they are used in
        ## TemplateAPI.
        self.config.testing_add_template('templates/form_macros.pt')
        self.config.testing_add_template('templates/master.pt')
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def _makeOne(self, context=None, request=None):
        from yait.views.utils import TemplateAPI
        if context is None:
            from repoze.bfg.testing import DummyModel
            context = DummyModel()
        if request is None:
            from repoze.bfg.testing import DummyRequest
            request = DummyRequest()
        return TemplateAPI(context, request)

    def test_request_related_attributes(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            environ=dict(HTTP_REFERER='http://referrer.com'))
        api = self._makeOne(request=request)
        self.assert_(api.request is request)
        self.assert_(api.app_url, 'http://example.com')
        self.assert_(api.here_url, 'http://example.com')
        self.assert_(api.referrer, 'http://referrer.com')
        self.assert_(api.show_login_link)

    def test_status_message(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            params=dict(status_message='A status message.'),
            environ=dict(HTTP_REFERER='http://example.com/foo'))
        api = self._makeOne(request=request)
        self.assertEqual(api.status_message, 'A status message.')

    def test_error_message(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            params=dict(error_message='An error message.'),
            environ=dict(HTTP_REFERER='http://example.com/foo'))
        api = self._makeOne(request=request)
        self.assertEqual(api.error_message, 'An error message.')

    def test_status_message_foreign(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            params=dict(status_message='A status message.'),
            environ=dict(HTTP_REFERER='http://other.com'))
        api = self._makeOne(request=request)
        self.assertEqual(api.status_message, '')

    def test_error_message_foreign(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            params=dict(error_message='An error message.'),
            environ=dict(HTTP_REFERER='http://other.com'))
        api = self._makeOne(request=request)
        self.assertEqual(api.error_message, '')

    def test_no_login_link_in_login_form(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            url='http://exemple.com/login_form?came_from=foo')
        api = self._makeOne(request=request)
        self.assert_(not api.show_login_link)

    def test_user_cn_anonymous(self):
        api = self._makeOne()
        self.assertEqual(api.user_cn, None)

    def test_user_cn_logged_in(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest(
            environ={'repoze.who.identity':
                         dict(uid=u'john.smith',
                              cn=u'John Smith')})
        api = self._makeOne(request=request)
        self.assertEqual(api.user_cn, u'John Smith')

    def test_misc_attributes(self):
        from repoze.bfg.testing import DummyRequest        
        request = DummyRequest()
        api = self._makeOne(request=request)
        self.assertEqual(api.header_prefix, u'Yait')
        self.assertEqual(api.html_title_prefix, u'Yait')
        self.assert_(getattr(api.layout, 'render', None) is not None)
        self.assert_(getattr(api.form_macros, 'render', None) is not None)

    def test_url_of(self):
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest()
        request.application_url = 'http://exemple.com'
        api = self._makeOne(request=request)
        self.assertEqual(api.url_of(''), 'http://exemple.com')
        self.assertEqual(api.url_of('foo'), 'http://exemple.com/foo')
        self.assertEqual(api.url_of('foo/bar'), 'http://exemple.com/foo/bar')
        self.assertEqual(api.url_of('foo/bar/'), 'http://exemple.com/foo/bar')

    def test_has_permission(self):
        from repoze.bfg.testing import DummyRequest
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
        from repoze.bfg.testing import DummyRequest
        request = DummyRequest()
        self.assertEqual(self._callFUT(request), {})

    def test_authenticated(self):
        from repoze.bfg.testing import DummyRequest
        md = dict(uid=u'john.smith', cn=u'John Smith')
        request = DummyRequest(environ={'repoze.who.identity': md})
        self.assertEqual(self._callFUT(request), md)


class TestHasPermission(TestCase):

    def setUp(self):
        pass ## FIXME: need anything here?

    def tearDown(self):
        pass ## FIXME: need anything here?

    def _callFUT(self, *args, **kwargs):
        from yait.views.utils import has_permission
        return has_permission(*args, **kwargs)

    def _makeRequest(self, user_id=None):
        from repoze.bfg.testing import DummyRequest
        environ={'repoze.who.identity': dict(uid=user_id)}
        return DummyRequest(environ=environ)

    def _makeProject(self, public=False):
        from yait.models import _getStore
        from yait.models import Project
        store = _getStore()
        p = Project(name=u'name', title=u'title', is_public=public)
        store.add(p)
        return p

    def _makeSiteAdmin(self, user_id):
        from yait.models import _getStore
        from yait.models import Manager
        store = _getStore()
        store.add(Manager(user_id=user_id))

    def test_unknown_permission(self):
        self.assertRaises(
            ValueError, self._callFUT,
            request=None, permission='Invalid permission')

    def test_invalid_permission_on_site(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        self.assertRaises(
            ValueError, self._callFUT,
            request=None, permission=PERM_ADMIN_PROJECT, context=None)

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

    def test_site_permission_for_site_manager(self):
        from yait.views.utils import PERM_ADMIN_SITE
        request = self._makeRequest(user_id=u'site_admin')
        self._makeSiteAdmin(u'site_admin')
        self.assert_(
            self._callFUT(request, PERM_ADMIN_SITE))

    def _test_role(self, user_id, project, **expected):
        ## An helper method for all 'test_role_*()' below
        from yait.views.utils import ALL_PERMS
        from yait.views.utils import PERM_VIEW_PROJECT
        from yait.views.utils import PERM_PARTICIPATE_IN_PROJECT
        from yait.views.utils import PERM_SEE_PRIVATE_TIMING_INFO
        from yait.views.utils import PERM_ADMIN_PROJECT
        missing_perms = set(ALL_PERMS).difference(expected.keys())
        assert not missing_perms, 'Some permissions are not tested!'
        request = self._makeRequest(user_id=user_id)
        for key, permission in dict(
            view=PERM_VIEW_PROJECT,
            participate=PERM_PARTICIPATE_IN_PROJECT,
            see_timing=PERM_SEE_PRIVATE_TIMING_INFO,
            admin_project=PERM_ADMIN_PROJECT).items():
            allowed = expected[key]
            self.assertEqual(
                self._callFUT(request, permission, project), allowed)

    def test_role_site_admin(self):
        self._makeSiteAdmin(u'admin')
        self._test_role(u'admin', None, dict(
                view=True,
                participate=True,
                see_timing=True,
                admin_project=True))

    def test_role_project_admin(self):
        from yait.views.utils import ROLE_PROJECT_ADMIN
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id, roles={project: ROLE_PROJECT_ADMIN})
        self._test_role(user_id, project, dict(
                view=True,
                participate=True,
                see_timing=True,
                admin_project=True))

    def test_role_project_internal_participant(self):
        from yait.views.utils import ROLE_PROJECT_INTERNAL_PARTICIPANT
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_INTERNAL_PARTICIPANT})
        self._test_role(user_id, project, dict(
                view=True,
                participate=True,
                see_timing=True,
                admin_project=False))

    def test_role_project_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_PARTICIPANT})
        self._test_role(user_id, project, dict(
                view=True,
                participate=True,
                see_timing=False,
                admin_project=False))

    def test_role_project_viewer(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id, roles={
                project: ROLE_PROJECT_VIEWER})
        self._test_role(user_id, project, dict(
                view=True,
                participate=False,
                see_timing=False,
                admin_project=False))

    def test_no_role(self):
        project = self._makeProject()
        user_id = u'user1'
        self._makeUser(user_id)
        self._test_role(user_id, project, dict(
                view=False,
                participate=False,
                see_timing=False,
                admin_project=False))

    def test_role_in_another_project(self):
        from yait.views.utils import PERM_ADMIN_PROJECT
        project1 = self._makeProject()
        project2 = self._makeProject()
        user_id = u'user1'
        ## give role on project 1
        self._makeUser(user_id, roles={project1: PERM_ADMIN_PROJECT})
        ## but check in project 2
        self._test_role(user_id, project2, dict(
                view=False,
                participate=False,
                see_timing=False,
                admin_project=False))

    def test_cache_site_permissions(self):
        pass ## FIXME: call has_permission once, then grant or revoke
             ## the role in the DB, then try has_permission again

    def test_cache_project_permissions(self):
        pass ## FIXME: call has_permission once, then grant or revoke
             ## the role in the DB, then try has_permission again


class TestRollbackTransaction(TestCase):

    def _callFUT(self, environ, status=None):
        from yait.views.utils import rollback_transaction
        return rollback_transaction(environ, status, None)

    def test_rollback_on_get(self):
        environ = dict(REQUEST_METHOD='GET')
        self.assertEqual(self._callFUT(environ), True)

    def test_rollback_when_4xx(self):
        environ = dict(REQUEST_METHOD='POST')
        self.assertEqual(self._callFUT(environ, '400'), True)

    def test_rollback_when_5xx(self):
        environ = dict(REQUEST_METHOD='POST')
        self.assertEqual(self._callFUT(environ, '500'), True)

    def test_commit_when_2xx(self):
        environ = dict(REQUEST_METHOD='POST')
        self.assertEqual(self._callFUT(environ, '200'), False)
