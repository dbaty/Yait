from yait.tests.base import TestCaseForViews


class TestControlPanelHome(TestCaseForViews):

    template_under_test = '../templates/control_panel.pt'

    def _call_fut(self, request):
        from yait.views.manage import control_panel
        return control_panel(request)

    def test_control_panel_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_control_panel_allow_admin(self):
        login = u'admin'
        self._make_user(login, is_admin=True)
        self._make_renderer()
        request = self._make_request(user=login)
        response = self._call_fut(request)
        self.assertEqual(response.status, '200 OK')


class TestListUsers(TestCaseForViews):

    template_under_test = '../templates/users.pt'

    def _call_fut(self, request):
        from yait.views.manage import list_users
        return list_users(request)

    def test_list_users_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_list_users_allow_admin(self):
        login = u'admin'
        admin = self._make_user(login, u'Admin One', is_admin=True)
        a2 = self._make_user(u'admin2', u'Admin Two', is_admin=True)
        u3 = self._make_user(u'user3', u'User Three')
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(users=[admin, a2, u3])


class TestAddUserForm(TestCaseForViews):

    template_under_test = '../templates/user_add.pt'

    def _call_fut(self, request):
        from yait.views.manage import add_user_form
        return add_user_form(request)

    def test_add_user_form_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_user_form(self):
        from yait.forms import AddUserForm
        login = u'admin'
        self._make_user(login, is_admin=True)
        request = self._make_request(user=login)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertIsInstance(renderer.form, AddUserForm)


class TestAddUser(TestCaseForViews):

    template_under_test = '../templates/user_add.pt'

    def _call_fut(self, request):
        from yait.views.manage import add_user
        return add_user(request)

    def test_add_user_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_user_allow_admin(self):
        from yait.models import User
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'login': u'jsmith',
                'password': u'secret',
                'password_confirm': u'secret',
                'fullname': u'John Smith',
                'email': u'jsmith@exemple.com'}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        self.assertEqual(len(request.get_flash('error')), 0)
        self.assertEqual(len(request.get_flash('success')), 1)
        self.assertEqual(self.session.query(User).count(), 2)
        user = self.session.query(User).filter_by(login=post['login']).one()
        self.assertEqual(user.login, post['login'])
        self.assertEqual(user.fullname, post['fullname'])
        self.assertEqual(user.email, post['email'])
        self.assert_(not user.is_admin)

    def test_add_user_invalid_form(self):
        from yait.models import User
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'login': u'',
                'password': u'',
                'password_confirm': u'',
                'fullname': u'',
                'email': u''}
        self._make_renderer()
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        self.assertEqual(self.session.query(User).count(), 1)


class TestEditUserForm(TestCaseForViews):

    template_under_test = '../templates/user_edit.pt'

    def _call_fut(self, request):
        from yait.views.manage import edit_user_form
        return edit_user_form(request)

    def test_edit_user_form_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_edit_user_form_unknown_user(self):
        from pyramid.httpexceptions import HTTPNotFound
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        matchdict = {'user_id': str(1 + admin.id)}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_edit_user_form(self):
        from yait.forms import EditUserForm
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        matchdict = {'user_id': str(admin.id)}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertIsInstance(renderer.form, EditUserForm)


class TestEditUser(TestCaseForViews):

    template_under_test = '../templates/user_edit.pt'

    def _call_fut(self, request):
        from yait.views.manage import edit_user
        return edit_user(request)

    def test_edit_user_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_edit_user_unknown_user(self):
        from pyramid.httpexceptions import HTTPNotFound
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        matchdict = {'user_id': str(1 + admin.id)}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_edit_user_incomplete_form(self):
        from yait.forms import EditUserForm
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        post = {}
        matchdict = {'user_id': str(admin.id)}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._call_fut(request)
        self.assertIsInstance(renderer.form, EditUserForm)
        self.assert_(len(renderer.form.errors))

    def test_edit_user_allow_admin(self):
        from yait.models import User
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        post = {'login': login,
                'fullname': u'John Smith',
                'email': u'jsmith@exemple.com',
                'is_admin': '1'}
        matchdict = {'user_id': str(admin.id)}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._call_fut(request)
        self.assertEqual(len(request.get_flash('error')), 0)
        self.assertEqual(len(request.get_flash('success')), 1)
        self.assertEqual(self.session.query(User).count(), 1)
        admin = self.session.query(User).filter_by(login=post['login']).one()
        self.assertEqual(admin.login, post['login'])
        self.assertEqual(admin.fullname, post['fullname'])
        self.assertEqual(admin.email, post['email'])
        self.assert_(admin.is_admin)

    def test_edit_user_cannot_revoke_own_s_admin_rights(self):
        from yait.models import User
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        post = {'login': admin.login,
                'fullname': u'John Smith',
                'email': u'jsmith@exemple.com'}
        matchdict = {'user_id': str(admin.id)}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        renderer = self._make_renderer()
        self._call_fut(request)
        # The 'edit_form' view is called, which creates a TemplateAPI,
        # which in turns pulls the notification from the session. This
        # is why we cannot use 'request.get_flash()'.
        self.assertEqual(len(renderer.api.notifications['error']), 1)
        self.assertEqual(len(renderer.api.notifications['success']), 0)
        admin = self.session.query(User).filter_by(login=login).one()
        self.assert_(admin.is_admin)


class TestListUserRoles(TestCaseForViews):

    template_under_test = '../templates/user_roles.pt'

    def _call_fut(self, request):
        from yait.views.manage import list_user_roles
        return list_user_roles(request)

    def test_list_user_roles_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_list_user_roles_reject_unknown_user(self):
        from pyramid.httpexceptions import HTTPNotFound
        login = u'admin'
        user = self._make_user(login, u'admin', is_admin=True)
        matchdict = {'user_id': str(1 + user.id)}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_list_user_roles_allow_admin(self):
        from yait.auth import ROLE_LABELS
        from yait.auth import ROLE_PROJECT_INTERNAL_PARTICIPANT
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        from yait.auth import ROLE_PROJECT_VIEWER
        p1 = self._make_project(u'p1')
        p2 = self._make_project(u'p2')
        p3 = self._make_project(u'p3')
        p4 = self._make_project(u'p4')
        self._make_project(u'p5')
        login = u'admin'
        user = self._make_user(login, u'admin', is_admin=True,
                               roles={p1: ROLE_PROJECT_INTERNAL_PARTICIPANT,
                                      p2: ROLE_PROJECT_MANAGER,
                                      p3: ROLE_PROJECT_PARTICIPANT,
                                      p4: ROLE_PROJECT_VIEWER})
        renderer = self._make_renderer()
        matchdict = {'user_id': str(user.id)}
        request = self._make_request(user=login, matchdict=matchdict)
        self._call_fut(request)
        renderer.assert_(user=user)
        expected_roles = [(p1, ROLE_LABELS[ROLE_PROJECT_INTERNAL_PARTICIPANT]),
                          (p2, ROLE_LABELS[ROLE_PROJECT_MANAGER]),
                          (p3, ROLE_LABELS[ROLE_PROJECT_PARTICIPANT]),
                          (p4, ROLE_LABELS[ROLE_PROJECT_VIEWER])]
        renderer.assert_(roles=expected_roles)


class TestListProjects(TestCaseForViews):

    template_under_test = '../templates/projects.pt'

    def _call_fut(self, request):
        from yait.views.manage import list_projects
        return list_projects(request)

    def test_list_projects_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_list_projects_allow_admin(self):
        login = u'admin'
        self._make_user(login, is_admin=True)
        p1 = self._make_project(u'p1', u'p1')
        p3 = self._make_project(u'p3', u'p3')
        p2 = self._make_project(u'p2', u'p2')
        renderer = self._make_renderer()
        request = self._make_request(user=login)
        self._call_fut(request)
        renderer.assert_(projects=[p1, p2, p3])


class TestProjectAddForm(TestCaseForViews):

    template_under_test = '../templates/project_add.pt'

    def _call_fut(self, request):
        from yait.views.manage import add_project_form
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
        self.assertIsInstance(renderer.form, AddProjectForm)


class TestAddProject(TestCaseForViews):

    template_under_test = '../templates/project_add.pt'

    def _call_fut(self, *args, **kwargs):
        from yait.views.manage import add_project
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
        self.assertIsInstance(renderer.form, AddProjectForm)
        self.assert_(len(renderer.form.errors))

    def test_add_project_name_already_taken(self):
        from yait.forms import AddProjectForm
        login = u'admin'
        self._make_user(login, is_admin=True)
        renderer = self._make_renderer()
        self._make_project(name=u'p1')
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        self.assertIsInstance(renderer.form, AddProjectForm)
        self.assert_(len(renderer.form.errors.get('name')))

    def test_add_project_allow_admin(self):
        from yait.models import Project
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'name': u'p1', 'title': u'Project 1', 'public': ''}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        projects = self.session.query(Project).all()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, u'p1')
        self.assertEqual(projects[0].title, u'Project 1')
        self.assertEqual(len(projects[0].statuses), 2)


class TestDeleteProject(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.manage import delete_project
        return delete_project(request)

    def test_delete_project_reject_not_admin(self):
        from pyramid.httpexceptions import HTTPForbidden
        request = self._make_request()
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_delete_project(self):
        from yait.models import Project
        p = self._make_project(u'p1', u'p1')
        login = u'admin'
        self._make_user(login, is_admin=True)
        post = {'project_id': p.id}
        request = self._make_request(user=login, post=post)
        self._call_fut(request)
        self.assertEqual(len(request.get_flash('error')), 0)
        self.assertEqual(len(request.get_flash('success')), 1)
        self.assertEqual(self.session.query(Project).all(), [])
