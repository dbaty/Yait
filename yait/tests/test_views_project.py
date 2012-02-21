"""Test views related to projects.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestProjectAddForm(TestCaseForViews):

    template_under_test = '../templates/project_add.pt'

    def _call_fut(self, request):
        from yait.views.project import add_project_form
        return add_project_form(request)

    def test_add_project_form_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_project_form_allow_admin(self):
        from yait.forms import AddProjectForm
        login = u'admin'
        self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        form = renderer._received.get('form', None)
        self.assertIsInstance(form, AddProjectForm)


class TestAddProject(TestCaseForViews):

    template_under_test = '../templates/project_add.pt'

    def _call_fut(self, *args, **kwargs):
        from yait.views.project import add_project
        return add_project(*args, **kwargs)

    def test_add_project_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_project_incomplete_form(self):
        from yait.forms import AddProjectForm
        login = u'admin'
        self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        post = {'name': u'p1', 'title': u''}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        form = renderer._received.get('form', None)
        self.assertIsInstance(form, AddProjectForm)
        self.assert_(len(form.errors))

    def test_add_project_name_already_taken(self):
        from yait.forms import AddProjectForm
        login = u'admin'
        self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        self._make_project(name=u'p1')
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        form = renderer._received.get('form', None)
        self.assertIsInstance(form, AddProjectForm)
        self.assert_(len(form.errors.get('name')))

    def test_add_project_allow_admin(self):
        from yait.models import Project
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assert_(location.endswith('/p1'))
        projects = self.session.query(Project).all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, u'p1')
        self.assertEqual(projects[0].title, u'Project 1')


class TestProjectHome(TestCaseForViews):

    template_under_test = '../templates/project.pt'

    def _call_fut(self, request):
        from yait.views.project import project_home
        return project_home(request)

    def test_project_view_unknowproject(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_view_disallowed(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_view_public_project(self):
        p = self._make_project(name=u'p1', public=True)
        renderer = self._make_renderer()
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self._call_fut(request)
        renderer.assert_(project=p)

    def test_project_view_allowed_user(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        renderer = self._make_renderer()
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self._call_fut(request)
        renderer.assert_(project=p)
