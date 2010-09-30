"""Test views related to projects.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestProjectAddForm(TestCaseForViews):

    template_under_test = 'templates/project_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.project import add_project_form
        return add_project_form(*args, **kwargs)

    def test_add_project_form_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_project_form_allow_admin(self):
        from yait.forms import AddProjectForm
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        form = renderer._received.get('form', None)
        self.assert_(isinstance(form, AddProjectForm))


class TestAddProject(TestCaseForViews):

    template_under_test = 'templates/project_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.project import add_project
        return add_project(*args, **kwargs)

    def test_add_project_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_project_incomplete_form(self):
        from yait.forms import AddProjectForm
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        context = self._makeModel()
        post = {'name': u'p1', 'title': u''}
        request = self._makeRequest(user_id=user_id, post=post)
        self._callFUT(context, request)
        form = renderer._received.get('form', None)
        self.assert_(isinstance(form, AddProjectForm))
        self.assert_(len(form.errors))

    def test_add_project_name_already_taken(self):
        from yait.forms import AddProjectForm
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        context = self._makeModel()
        self._makeProject(name=u'p1')
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._makeRequest(user_id=user_id, post=post)
        self._callFUT(context, request)
        form = renderer._received.get('form', None)
        self.assert_(isinstance(form, AddProjectForm))
        self.assert_(len(form.errors.get('name')))

    def test_add_project_allow_admin(self):
        from yait.models import Project
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_(location.endswith('/p1'))
        projects = self.session.query(Project).all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, u'p1')
        self.assertEqual(projects[0].title, u'Project 1')


class TestViewProject(TestCaseForViews):

    template_under_test = 'templates/project_view.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.project import project_view
        return project_view(*args, **kwargs)

    def test_project_view_unknowproject(self):
        context = self._makeModel()
        matchdict = {'project_name': u'unknown'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_project_view_disallowed(self):
        self._makeProject(name=u'p1')
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_project_view_public_project(self):
        p = self._makeProject(name=u'p1', public=True)
        renderer = self._makeRenderer()
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(matchdict=matchdict)
        self._callFUT(context, request)
        renderer.assert_(project=p)

    def test_project_view_allowed_user(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        renderer = self._makeRenderer()
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        self._callFUT(context, request)
        renderer.assert_(project=p)
