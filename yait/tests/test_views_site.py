"""Test views related to the site.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestSiteIndex(TestCaseForViews):

    template_under_test = 'templates/site_index.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import site_index
        return site_index(*args, **kwargs)

    def test_site_index_no_project(self):
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest()
        self._callFUT(context, request)
        renderer.assert_(projects=[])

    def test_site_index_projects_for_anonymous_user(self):
        self._makeProject(name=u'private', title=u'p')
        public_project = self._makeProject(
            name=u'public', title=u'p', public=True)
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest()
        self._callFUT(context, request)
        renderer.assert_(projects=[public_project])

    def test_site_index_projects_for_logged_in_user(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        public_project = self._makeProject(
            name=u'public', title=u'public', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        self._makeProject(name=u'p2', title=u'p2')
        user_id = u'user'
        self._makeUser(user_id, roles={p1: ROLE_PROJECT_VIEWER})
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        renderer.assert_(projects=[p1, public_project])

    def test_site_index_projects_for_site_admin(self):
        public_project = self._makeProject(
            name=u'public', title=u'p3', public=True)
        p1 = self._makeProject(name=u'p1', title=u'p1')
        p2 = self._makeProject(name=u'p2', title=u'p2')
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        renderer.assert_(projects=[p1, p2, public_project])


class TestSiteControlPanel(TestCaseForViews):

    template_under_test = 'templates/site_control_panel.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import control_panel
        return control_panel(*args, **kwargs)

    def test_control_panel_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_control_panel_allow_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '200 OK')


class TestManageAdminsForm(TestCaseForViews):
    
    template_under_test = 'templates/site_manage_admins_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import manage_admins_form
        return manage_admins_form(*args, **kwargs)

    def test_manage_admins_form_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_manage_admins_form_allow_admin(self):
        user_id = u'admin'
        admin = self._makeSiteAdmin(user_id)
        a3 = self._makeSiteAdmin('admin3')
        a2 = self._makeSiteAdmin('admin2')
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        renderer.assert_(current_user_id=user_id)
        renderer.assert_(admins=[admin, a2, a3])


class TestAddAdmin(TestCaseForViews):

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import add_admin
        return add_admin(*args, **kwargs)

    def test_add_admin_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_admin_no_user_id(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(admin_id=u'')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_add_admin_already_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(admin_id=u'admin')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_add_admin_success(self):
        from yait.models import Admin
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(admin_id=u'admin2')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        admins = [a.user_id for a in \
                      self.session.query(Admin).order_by('user_id').all()]
        self.assertEqual(admins, [u'admin', u'admin2'])


class TestDeleteAdmin(TestCaseForViews):

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import delete_admin
        return delete_admin(*args, **kwargs)

    def test_delete_admin_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_admin_himself(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(admin_id=user_id)
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_delete_admin_no_user_id(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(admin_id=u'')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_delete_admin_success(self):
        from yait.models import Admin
        user_id = u'admin'
        admin = self._makeSiteAdmin(user_id)
        self._makeSiteAdmin(u'admin2')
        context = self._makeModel()
        post = dict(admin_id=u'admin2')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        self.assertEqual(self.session.query(Admin).all(), [admin])


class TestManageProjectsForm(TestCaseForViews):

    template_under_test = 'templates/site_manage_projects_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import manage_projects_form
        return manage_projects_form(*args, **kwargs)

    def test_manage_projects_form_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_manage_projects_form_allow_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        p1 = self._makeProject(u'p1', u'p1')
        p3 = self._makeProject(u'p3', u'p3')
        p2 = self._makeProject(u'p2', u'p2')
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        renderer.assert_(projects=[p1, p2, p3])


class TestDeleteProject(TestCaseForViews):

    def _callFUT(self, *args, **kwargs):
        from yait.views.site import delete_project
        return delete_project(*args, **kwargs)

    def test_delete_project_reject_not_admin(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_project(self):
        from yait.models import Project
        p = self._makeProject(u'p1', u'p1')
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        context = self._makeModel()
        post = dict(project_id=p.id)
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        self.assertEqual(self.session.query(Project).all(), [])


class TestNotFound(TestCaseForViews):

    def test_not_found(self):
        from yait.views.site import not_found
        context = self._makeModel()
        request = self._makeRequest()
        response = not_found(context, request)
        self.assert_(response.status, '404 Not Found')
