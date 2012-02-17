"""Test views related to the site.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestSiteHome(TestCaseForViews):

    template_under_test = 'templates/site_home.pt'

    def _callFUT(self, request):
        from yait.views.site import home
        return home(request)

    def test_site_home_no_project(self):
        renderer = self._makeRenderer()
        request = self._makeRequest()
        self._callFUT(request)
        renderer.assert_(projects=[])

    def test_site_home_projects_for_anonymous_user(self):
        self._makeProject(name=u'private', title=u'p')
        public_project = self._makeProject(
            name=u'public', title=u'p', public=True)
        renderer = self._makeRenderer()
        request = self._makeRequest()
        self._callFUT(request)
        renderer.assert_(projects=[public_project])

    def test_site_home_projects_for_logged_in_user(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        public_project = self._makeProject(
            name=u'public', title=u'public', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        self._makeProject(name=u'p2', title=u'p2')
        user_id = u'user'
        self._makeUser(user_id, roles={p1: ROLE_PROJECT_VIEWER})
        renderer = self._makeRenderer()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(request)
        renderer.assert_(projects=[p1, public_project])

    def test_site_home_projects_for_site_admin(self):
        public_project = self._makeProject(
            name=u'public', title=u'p3', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        p2 = self._makeProject(name=u'p2', title=u'p2')
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(request)
        renderer.assert_(projects=[p1, p2, public_project])


class TestNotFound(TestCaseForViews):

    def test_not_found(self):
        from yait.views.site import not_found
        request = self._makeRequest()
        response = not_found(request)
        self.assert_(response.status, '404 Not Found')
