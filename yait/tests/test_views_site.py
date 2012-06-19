from yait.tests.base import TestCaseForViews


class TestSiteHome(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.site import home
        return home(request)

    def test_site_home_no_project(self):
        request = self._make_request()
        res = self._call_fut(request)
        self.assertEqual(res['projects'], [])

    def test_site_home_projects_for_anonymous_user(self):
        self._make_project(name=u'private', title=u'p')
        public_project = self._make_project(
            name=u'public', title=u'p', public=True)
        request = self._make_request()
        res = self._call_fut(request)
        self.assertEqual(res['projects'], [public_project])

    def test_site_home_projects_for_logged_in_user(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        public_project = self._make_project(
            name=u'public', title=u'public', public=True)
        p1 = self._make_project(name=u'p1', title=u'p1')
        self._make_project(name=u'p2', title=u'p2')
        login = u'user'
        self._make_user(login, roles={p1: ROLE_PROJECT_VIEWER})
        request = self._make_request(user=login)
        res = self._call_fut(request)
        self.assertEqual(res['projects'], [p1, public_project])

    def test_site_home_projects_for_site_admin(self):
        public_project = self._make_project(
            name=u'public', title=u'p3', public=True)
        p1 = self._make_project(name=u'p1', title=u'p1')
        p2 = self._make_project(name=u'p2', title=u'p2')
        login = u'admin'
        self._make_user(login, is_admin=True)
        request = self._make_request(user=login)
        res = self._call_fut(request)
        self.assertEqual(res['projects'], [p1, p2, public_project])


class TestNotFound(TestCaseForViews):

    def test_not_found(self):
        from yait.views.site import not_found
        request = self._make_request()
        not_found(request)
        self.assert_(request.response.status, '404 Not Found')
