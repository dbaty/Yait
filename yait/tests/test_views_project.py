from yait.tests.base import TestCaseForViews


class TestProjectHome(TestCaseForViews):

    template_under_test = '../templates/project.pt'

    def _call_fut(self, request):
        from yait.views.project import home
        return home(request)

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
        from yait.auth import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        renderer = self._make_renderer()
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self._call_fut(request)
        renderer.assert_(project=p)
