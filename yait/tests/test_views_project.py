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


class TestProjectConfigureForm(TestCaseForViews):

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
        project = self._make_project(name=u'project')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        self._make_user(u'admin', is_admin=True)
        matchdict = {'project_name': project.name}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(renderer.form.data['title'], project.title)


class TestProjectConfigure(TestCaseForViews):

    template_under_test = '../templates/project_configure.pt'

    def _call_fut(self, request):
        from yait.views.project import configure
        return configure(request)

    def test_project_config_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_config_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_config_manager(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        project = self._make_project(name=u'project')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        self._make_user(u'admin', is_admin=True)
        matchdict = {'project_name': project.name}
        post = {'title': u'New title'}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._call_fut(request)
        self.assertEqual(project.title, u'New title')

    def test_project_config_manager_cannot_change_name(self):
        # The name of a project cannot be changed.
        from yait.auth import ROLE_PROJECT_MANAGER
        project = self._make_project(name=u'project')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        self._make_user(u'admin', is_admin=True)
        matchdict = {'project_name': project.name}
        post = {'title': project.title, 'name': u'new-name'}
        request = self._make_request(user=login, matchdict=matchdict, post=post)
        self._call_fut(request)
        self.assertEqual(project.name, u'project')


class TestProjectConfigureRolesForm(TestCaseForViews):

    template_under_test = '../templates/project_roles.pt'

    def _call_fut(self, request):
        from yait.views.project import configure_roles_form
        return configure_roles_form(request)

    def test_project_config_roles_form_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_config_roles_form_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_config_roles_form_manager(self):
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

    def test_project_config_roles_form_admin_sees_all_users_with_no_role(self):
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


class TestProjectConfigureRoles(TestCaseForViews):

    template_under_test = '../templates/project_roles.pt'

    def _call_fut(self, request):
        from yait.views.project import configure_roles
        return configure_roles(request)

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


class TestProjectConfigureStatusesForm(TestCaseForViews):

    template_under_test = '../templates/project_statuses.pt'

    def _call_fut(self, request):
        from yait.views.project import configure_statuses_form
        return configure_statuses_form(request)

    def test_project_config_statuses_form_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_config_statuses_form_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_config_statuses_form_manager(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        project = self._make_project(name=u'p1')
        used_status = project.statuses[0].id
        self._make_issue(project, status=used_status)
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        renderer.assert_(used=[used_status])


class TestProjectConfigureStatuses(TestCaseForViews):

    template_under_test = '../templates/project_statuses.pt'

    def _call_fut(self, request):
        from yait.views.project import configure_statuses
        return configure_statuses(request)

    def test_project_config_statuses_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'unknown'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_project_config_statuses_not_manager(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_project_config_statuses_manager_reorder(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.models import ISSUE_STATUS_CLOSED
        from yait.models import ISSUE_STATUS_CLOSED_LABEL
        from yait.models import ISSUE_STATUS_OPEN
        from yait.models import ISSUE_STATUS_OPEN_LABEL
        from yait.models import Project
        project = self._make_project(name=u'p1')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        post = (('statuses', unicode(ISSUE_STATUS_CLOSED)),
                ('statuses', unicode(ISSUE_STATUS_OPEN)),
                ('labels', ISSUE_STATUS_CLOSED_LABEL),
                ('labels', ISSUE_STATUS_OPEN_LABEL))
        request = self._make_request(user=login, post=post, matchdict=matchdict)
        label_of = lambda statuses: [s.label for s in statuses]
        self.assertEqual(label_of(project.statuses), ['open', 'closed'])
        self._call_fut(request)
        # We need to detach 'project' from the session, otherwise
        # SQLAlchemy does not retrieve statuses again when we access
        # 'p.statuses'.
        self.session.expunge(project)
        project = self.session.query(Project).one()
        self.assertEqual(label_of(project.statuses), ['closed', 'open'])

    def test_project_config_statuses_manager_change_label(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.models import ISSUE_STATUS_CLOSED
        from yait.models import ISSUE_STATUS_CLOSED_LABEL
        from yait.models import ISSUE_STATUS_OPEN
        from yait.models import ISSUE_STATUS_OPEN_LABEL
        from yait.models import Project
        project = self._make_project(name=u'p1')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        new_open_label = '%s-edited' % ISSUE_STATUS_OPEN_LABEL
        new_closed_label = '%s-edited' % ISSUE_STATUS_CLOSED_LABEL
        post = (('statuses', unicode(ISSUE_STATUS_OPEN)),
                ('statuses', unicode(ISSUE_STATUS_CLOSED)),
                ('labels', new_open_label),
                ('labels', new_closed_label))
        request = self._make_request(user=login, post=post, matchdict=matchdict)
        label_of = lambda statuses: [s.label for s in statuses]
        self.assertEqual(label_of(project.statuses), ['open', 'closed'])
        self._call_fut(request)
        # We need to detach 'project' from the session, otherwise
        # SQLAlchemy does not retrieve statuses again when we access
        # 'p.statuses'.
        self.session.expunge(project)
        project = self.session.query(Project).one()
        self.assertEqual(label_of(project.statuses),
                         [new_open_label, new_closed_label])
        # FIXME: check that the 'statuses' cache has been refreshed
        # (or at least invalidated).

    def test_project_config_statuses_manager_add_status(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.models import ISSUE_STATUS_CLOSED
        from yait.models import ISSUE_STATUS_CLOSED_LABEL
        from yait.models import ISSUE_STATUS_OPEN
        from yait.models import ISSUE_STATUS_OPEN_LABEL
        from yait.models import Project
        project = self._make_project(name=u'p1')
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        new_status = u'new status'
        post = (('statuses', unicode(ISSUE_STATUS_OPEN)),
                ('statuses', '0'),
                ('statuses', unicode(ISSUE_STATUS_CLOSED)),
                ('labels', ISSUE_STATUS_OPEN_LABEL),
                ('labels', new_status),
                ('labels', ISSUE_STATUS_CLOSED_LABEL))
        request = self._make_request(user=login, post=post, matchdict=matchdict)
        label_of = lambda statuses: [s.label for s in statuses]
        self.assertEqual(label_of(project.statuses), ['open', 'closed'])
        self._call_fut(request)
        # We need to detach 'project' from the session, otherwise
        # SQLAlchemy does not retrieve statuses again when we access
        # 'p.statuses'.
        self.session.expunge(project)
        project = self.session.query(Project).one()
        self.assertEqual(label_of(project.statuses),
                         ['open', new_status, 'closed'])

    def test_project_config_statuses_manager_remove_unused_status(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.models import ISSUE_STATUS_CLOSED
        from yait.models import ISSUE_STATUS_CLOSED_LABEL
        from yait.models import ISSUE_STATUS_OPEN
        from yait.models import ISSUE_STATUS_OPEN_LABEL
        from yait.models import Project
        from yait.models import Status
        project = self._make_project(name=u'p1')
        label = u'status to remove'
        self.session.add(Status(id=4, project_id=project.id,
                                label=label, position=3))
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        post = (('statuses', unicode(ISSUE_STATUS_OPEN)),
                ('statuses', unicode(ISSUE_STATUS_CLOSED)),
                ('labels', ISSUE_STATUS_OPEN_LABEL),
                ('labels', ISSUE_STATUS_CLOSED_LABEL))
        request = self._make_request(user=login, post=post, matchdict=matchdict)
        label_of = lambda statuses: [s.label for s in statuses]
        self.assertEqual(label_of(project.statuses), ['open', 'closed', label])
        self._call_fut(request)
        # We need to detach 'project' from the session, otherwise
        # SQLAlchemy does not retrieve statuses again when we access
        # 'p.statuses'.
        self.session.expunge(project)
        project = self.session.query(Project).one()
        self.assertEqual(label_of(project.statuses), ['open', 'closed'])

    def test_project_config_statuses_manager_cannot_remove_used_status(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.models import ISSUE_STATUS_CLOSED
        from yait.models import ISSUE_STATUS_CLOSED_LABEL
        from yait.models import ISSUE_STATUS_OPEN
        from yait.models import Project
        project = self._make_project(name=u'p1')
        self._make_issue(project, status=ISSUE_STATUS_OPEN)
        login = u'manager'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        matchdict = {'project_name': u'p1'}
        post = (('statuses', unicode(ISSUE_STATUS_CLOSED)),
                ('labels', ISSUE_STATUS_CLOSED_LABEL))
        request = self._make_request(user=login, post=post, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(len(renderer.api.notifications['error']), 1)
        # We need to detach 'project' from the session, otherwise
        # SQLAlchemy does not retrieve statuses again when we access
        # 'p.statuses'.
        self.session.expunge(project)
        project = self.session.query(Project).one()
        label_of = lambda statuses: [s.label for s in statuses]
        self.assertEqual(label_of(project.statuses), ['open', 'closed'])
