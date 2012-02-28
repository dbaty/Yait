from yait.tests.base import TestCaseForViews


class TestSiteHome(TestCaseForViews):

    template_under_test = '../templates/home.pt'

    def _call_fut(self, request):
        from yait.views.site import home
        return home(request)

    def test_site_home_no_project(self):
        renderer = self._make_renderer()
        request = self._make_request()
        self._call_fut(request)
        renderer.assert_(projects=[])

    def test_site_home_projects_for_anonymous_user(self):
        self._make_project(name=u'private', title=u'p')
        public_project = self._make_project(
            name=u'public', title=u'p', public=True)
        renderer = self._make_renderer()
        request = self._make_request()
        self._call_fut(request)
        renderer.assert_(projects=[public_project])

    def test_site_home_projects_for_logged_in_user(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        public_project = self._make_project(
            name=u'public', title=u'public', public=True)
        p1 = self._make_project(name=u'p1', title=u'p1')
        self._make_project(name=u'p2', title=u'p2')
        login = u'user'
        self._make_user(login, roles={p1: ROLE_PROJECT_VIEWER})
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(projects=[p1, public_project])

    def test_site_home_projects_for_site_admin(self):
        public_project = self._make_project(
            name=u'public', title=u'p3', public=True)
        p1 = self._make_project(name=u'p1', title=u'p1')
        p2 = self._make_project(name=u'p2', title=u'p2')
        login = u'admin'
        self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(projects=[p1, p2, public_project])


class TestNotFound(TestCaseForViews):

    template_under_test = '../templates/notfound.pt'

    def test_not_found(self):
        from yait.views.site import not_found
        self._make_renderer()
        request = self._make_request()
        response = not_found(request)
        self.assert_(response.status, '404 Not Found')
