from yait.tests.base import TestCaseForViews


class TestSiteControlPanel(TestCaseForViews):

    template_under_test = 'templates/site_control_panel.pt'

    def _callFUT(self, request):
        from yait.views.manage import control_panel
        return control_panel(request)

    def test_control_panel_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_control_panel_allow_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        request = self._makeRequest(user_id=user_id)
        response = self._callFUT(request)
        self.assertEqual(response.status, '200 OK')


class TestListAdmin(TestCaseForViews):

    # FIXME: rename
    template_under_test = 'templates/site_manage_admins_form.pt'

    def _callFUT(self, request):
        from yait.views.manage import list_admins
        return list_admins(request)

    def test_list_admins_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_list_admins_allow_admin(self):
        user_id = u'admin'
        admin = self._makeSiteAdmin(user_id)
        a3 = self._makeSiteAdmin('admin3')
        a2 = self._makeSiteAdmin('admin2')
        renderer = self._makeRenderer()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(request)
        renderer.assert_(current_user_id=user_id)
        renderer.assert_(admins=[admin, a2, a3])


class TestAddAdmin(TestCaseForViews):

    def _callFUT(self, request):
        from yait.views.manage import add_admin
        return add_admin(request)

    def test_add_admin_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_admin_no_user_id(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'admin_id': u''}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_add_admin_already_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'admin_id': u'admin'}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_add_admin_success(self):
        from yait.models import Admin
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'admin_id': u'admin2'}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        admins = [a.user_id for a in \
                      self.session.query(Admin).order_by('user_id').all()]
        self.assertEqual(admins, [u'admin', u'admin2'])


class TestDeleteAdmin(TestCaseForViews):

    def _callFUT(self, request):
        from yait.views.manage import delete_admin
        return delete_admin(request)

    def test_delete_admin_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_admin_himself(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'admin_id': user_id}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_delete_admin_no_user_id(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'admin_id': u''}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('error_message' in location)

    def test_delete_admin_success(self):
        from yait.models import Admin
        user_id = u'admin'
        admin = self._makeSiteAdmin(user_id)
        self._makeSiteAdmin(u'admin2')
        post = {'admin_id': u'admin2'}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        self.assertEqual(self.session.query(Admin).all(), [admin])


class TestListProjects(TestCaseForViews):

    # FIXME: rename template
    template_under_test = 'templates/site_manage_projects_form.pt'

    def _callFUT(self, request):
        from yait.views.manage import list_projects
        return list_projects(request)

    def test_list_projects_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_list_projects_allow_admin(self):
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        p1 = self._makeProject(u'p1', u'p1')
        p3 = self._makeProject(u'p3', u'p3')
        p2 = self._makeProject(u'p2', u'p2')
        renderer = self._makeRenderer()
        request = self._makeRequest(user_id=user_id)
        self._callFUT(request)
        renderer.assert_(projects=[p1, p2, p3])


class TestDeleteProject(TestCaseForViews):

    def _callFUT(self, *args, **kwargs):
        from yait.views.manage import delete_project
        return delete_project(*args, **kwargs)

    def test_delete_project_reject_not_admin(self):
        request = self._makeRequest()
        response = self._callFUT(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_project(self):
        from yait.models import Project
        p = self._makeProject(u'p1', u'p1')
        user_id = u'admin'
        self._makeSiteAdmin(user_id)
        post = {'project_id': p.id}
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(request)
        location = response.headers['Location']
        self.assert_('status_message' in location)
        self.assertEqual(self.session.query(Project).all(), [])
