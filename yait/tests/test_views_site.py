"""Test views related to the site.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestSiteIndex(TestCaseForViews):

    template_under_test = 'templates/site_index.pt'

    def test_no_project(self):
        from yait.views.site import site_index
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest()
        site_index(context, request)
        renderer.assert_(projects=[])

    def test_projects_for_anonymous_user(self):
        from yait.views.site import site_index
        self._makeProject(name=u'private', title=u'p')
        public_project = self._makeProject(
            name=u'public', title=u'p', public=True)
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest()
        site_index(context, request)
        renderer.assert_(projects=[public_project])

    def test_projects_for_logged_in_user(self):
        from yait.views.site import site_index
        from yait.views.utils import ROLE_PROJECT_VIEWER
        public_project = self._makeProject(
            name=u'public', title=u'public', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        self._makeProject(name=u'p2', title=u'p2')
        user_id = u'user'
        self._makeUser(user_id, roles={p1: ROLE_PROJECT_VIEWER})
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id)
        site_index(context, request)
        renderer.assert_(projects=[p1, public_project])

    def test_projects_for_site_admin(self):
        from yait.views.site import site_index
        public_project = self._makeProject(
            name=u'public', title=u'p3', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        p2 = self._makeProject(name=u'p2', title=u'p2')
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id)
        site_index(context, request)
        renderer.assert_(projects=[p1, p2, public_project])


class TestSiteControlPanel(TestCaseForViews):

    template_under_test = 'templates/site_control_panel.pt'

    def test_allow_admin(self):
        from yait.views.site import control_panel
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        request = self._makeRequest(user_id)
        response = control_panel(context, request)
        self.assertEqual(response.status, '200 OK')

    def test_reject_not_admin(self):
        from yait.views.site import control_panel
        context = self._makeModel()
        request = self._makeRequest()
        response = control_panel(context, request)
        self.assertEqual(response.status, '401 Unauthorized')


class TestManageAdminsForm(TestCaseForViews):
    
    template_under_test = 'templates/site_manage_admins_form'
