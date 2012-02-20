from yait.tests.base import TestCaseForViews


class TestSiteControlPanel(TestCaseForViews):

    template_under_test = '../templates/site_control_panel.pt'

    def _call_fut(self, request):
        from yait.views.manage import control_panel
        return control_panel(request)

    def test_control_panel_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_control_panel_allow_admin(self):
        login = u'admin'
        self._make_user(login, is_admin=True)
        request = self._make_request(user=login)
        response = self._call_fut(request)
        self.assertEqual(response.status, '200 OK')


class TestListAdmin(TestCaseForViews):

    template_under_test = '../templates/list_admins.pt'

    def _call_fut(self, request):
        from yait.views.manage import list_admins
        return list_admins(request)

    def test_list_admins_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_list_admins_allow_admin(self):
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        a3 = self._make_user('admin3', is_admin=True)
        a2 = self._make_user('admin2', is_admin=True)
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(current_user_id=admin.id)
        renderer.assert_(admins=[admin, a2, a3])


class TestAddAdmin(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.manage import add_admin
        return add_admin(request)

    def test_add_admin_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_admin_no_user_id(self):
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'admin_id': u''}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('error_message', location)

    def test_add_admin_already_admin(self):
        login = u'admin'
        self._make_user(login)
        post = {'admin_id': u'admin'}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('error_message', location)

    def test_add_admin_success(self):
        from yait.models import Admin
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'admin_id': u'admin2'}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('status_message', location)
        admins = [a.user_id for a in \
                      self.session.query(Admin).order_by('user_id').all()]
        self.assertEqual(admins, [u'admin', u'admin2'])


class TestDeleteAdmin(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.manage import delete_admin
        return delete_admin(request)

    def test_delete_admin_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_admin_himself(self):
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        post = {'admin_id': admin.id}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('error_message', location)

    def test_delete_admin_no_user_id(self):
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'admin_id': u''}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('error_message', location)

    def test_delete_admin_success(self):
        from yait.models import Admin
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        admin2 = self._make_user(u'admin2', is_admin=True)
        post = {'admin_id': admin2.id}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('status_message', location)
        self.assertEqual(self.session.query(Admin).all(), [admin])


class TestListProjects(TestCaseForViews):

    template_under_test = '../templates/list_projects.pt'

    def _call_fut(self, request):
        from yait.views.manage import list_projects
        return list_projects(request)

    def test_list_projects_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_list_projects_allow_admin(self):
        login = u'admin'
        self._make_user(login)
        p1 = self._make_project(u'p1', u'p1')
        p3 = self._make_project(u'p3', u'p3')
        p2 = self._make_project(u'p2', u'p2')
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(projects=[p1, p2, p3])


class TestDeleteProject(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.manage import delete_project
        return delete_project(request)

    def test_delete_project_reject_not_admin(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_delete_project(self):
        from yait.models import Project
        p = self._make_project(u'p1', u'p1')
        login = u'admin'
        self._make_user(login)
        post = {'project_id': p.id}
        request = self._make_request(user=login, post=post)
        response = self._call_fut(request)
        location = response.headers['Location']
        self.assertIn('status_message', location)
        self.assertEqual(self.session.query(Project).all(), [])
