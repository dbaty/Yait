from yait.tests.base import TestCaseForViews


class TestProjectHome(TestCaseForViews):

    template_under_test = '../templates/project.pt'

    def _call_fut(self, request):
        from yait.views.project import home
        return home(request)

    def test_project_view_unknown_project(self):
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


class TestProjectConfigure(TestCaseForViews):

    template_under_test = '../templates/project_configure.pt'

    def _call_fut(self, request):
        from yait.views.project import configure_form
        return configure_form(request)

    def test_project_config_form_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_config_form_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_config_form_manager(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_VIEWER
        project1 = self._make_project(name=u'p1')
        project2 = self._make_project(name=u'p2')
        login = u'manager1'
        manager1 = self._make_user(login,
                                   roles={project1: ROLE_PROJECT_MANAGER})
        manager2 = self._make_user(u'manager2',
                                   roles={project1: ROLE_PROJECT_MANAGER})
        viewer = self._make_user(u'viewer',
                                 roles={project1: ROLE_PROJECT_VIEWER})
        self._make_user(u'no_role_in_project1',
                        roles={project2: ROLE_PROJECT_VIEWER})
        self._make_user(u'admin', is_admin=True)
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(renderer.project, project1)
        user_roles = [{'user_id': manager1.id,
                       'fullname': manager1.fullname,
                       'role': ROLE_PROJECT_MANAGER},
                      {'user_id': manager2.id,
                       'fullname': manager2.fullname,
                       'role': ROLE_PROJECT_MANAGER},
                      {'user_id': viewer.id,
                       'fullname': viewer.fullname,
                       'role': ROLE_PROJECT_VIEWER}]
        self.assertEqual(renderer.user_roles, user_roles)
        self.assertEqual(renderer.users_with_no_role, ())

    def test_project_config_form_admin_sees_all_users_with_no_role(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        project1 = self._make_project(name=u'p1')
        project2 = self._make_project(name=u'p2')
        login = u'admin1'
        self._make_user(login=login, is_admin=True)
        self._make_user(login=u'admin2', is_admin=True)
        self._make_user(u'viewer', roles={project1: ROLE_PROJECT_VIEWER})
        no_role = self._make_user(u'no_role_in_project1',
                                  roles={project2: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(renderer.project, project1)
        users_with_no_role = [{'id': 0,
                               'fullname': u'Select a user...'},
                              {'id': no_role.id,
                               'fullname': no_role.fullname}]
        self.assertEqual(renderer.users_with_no_role, users_with_no_role)


class TestUpdateRoles(TestCaseForViews):

    template_under_test = '../templates/project_configure.pt'

    def _call_fut(self, request):
        from yait.views.project import update_roles
        return update_roles(request)

    def test_project_update_roles_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_update_roles_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_update_roles_allow_manager(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        from yait.auth import ROLE_PROJECT_VIEWER
        from yait.models import Role
        project = self._make_project(name=u'p1')
        login = u'manager'
        self._make_user(login=login, roles={project: ROLE_PROJECT_MANAGER})
        user2 = self._make_user(login=u'user2',
                                roles={project: ROLE_PROJECT_PARTICIPANT})
        matchdict = {'project_name': u'p1'}
        post = {'role_%d' % user2.id: ROLE_PROJECT_VIEWER}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._make_renderer()
        self._call_fut(request)
        self.assertEqual(len(request.get_flash('error')), 0)
        self.assertEqual(len(request.get_flash('success')), 1)
        role = self.session.query(Role).filter_by(user_id=user2.id).one()
        self.assertEqual(role.role, ROLE_PROJECT_VIEWER)

    def test_project_update_roles_manager_refuse_to_revoke_own_role(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_VIEWER
        from yait.models import Role
        project = self._make_project(name=u'p1')
        login = u'manager'
        manager = self._make_user(login=login,
                                  roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        post = {'role_%d' % manager.id: ROLE_PROJECT_VIEWER}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        renderer = self._make_renderer()
        self._call_fut(request)
        # The 'configure_form' view is called, which creates a
        # TemplateAPI, which in turns pulls the notification from the
        # session. This is why we cannot use 'request.get_flash()'.
        self.assertEqual(len(renderer.api.notifications['error']), 1)
        self.assertEqual(len(renderer.api.notifications['success']), 0)
        role = self.session.query(Role).filter_by(user_id=manager.id).one()
        self.assertEqual(role.role, ROLE_PROJECT_MANAGER)

    def test_project_update_roles_manager_refuse_new_user(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_VIEWER
        from yait.models import Role
        project = self._make_project(name=u'p1')
        login = u'manager'
        self._make_user(login=login, roles={project: ROLE_PROJECT_MANAGER})
        user = self._make_user(login=u'user')
        matchdict = {'project_name': u'p1'}
        post = {'role_%d' % user.id: ROLE_PROJECT_VIEWER}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        renderer = self._make_renderer()
        self._call_fut(request)
        # The 'configure_form' view is called, which creates a
        # TemplateAPI, which in turns pulls the notification from the
        # session. This is why we cannot use 'request.get_flash()'.
        self.assertEqual(len(renderer.api.notifications['error']), 1)
        self.assertEqual(len(renderer.api.notifications['success']), 0)
        role = self.session.query(Role).filter_by().one()
        self.assertEqual(role.role, ROLE_PROJECT_MANAGER)

    def test_project_update_roles_allow_admin_to_grant_to_new_user(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        from yait.models import Role
        self._make_project(name=u'p1')
        login = u'admin'
        self._make_user(login=login, is_admin=True)
        user = self._make_user(login=u'user')
        matchdict = {'project_name': u'p1'}
        post = {'role_%d' % user.id: ROLE_PROJECT_VIEWER}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._call_fut(request)
        # The 'configure_form' view is called, which creates a
        # TemplateAPI, which in turns pulls the notification from the
        # session. This is why we cannot use 'request.get_flash()'.
        self.assertEqual(len(request.get_flash('error')), 0)
        self.assertEqual(len(request.get_flash('success')), 1)
        role = self.session.query(Role).filter_by().one()
        self.assertEqual(role.role, ROLE_PROJECT_VIEWER)
        self.assertEqual(role.user_id, user.id)
