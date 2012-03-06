from yait.tests.base import TestCaseForViews


class TestHasPermission(TestCaseForViews):

    def _call_fut(self, *args, **kwargs):
        from yait.auth import has_permission
        return has_permission(*args, **kwargs)

    def test_unknown_permission(self):
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission='Invalid permission')

    def test_invalid_permission_on_site(self):
        from yait.auth import PERM_MANAGE_PROJECT
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission=PERM_MANAGE_PROJECT, context=None)

    def test_invalid_permission_on_project(self):
        from yait.auth import PERM_ADMIN_SITE
        project = self._make_project()
        self.assertRaises(
            ValueError, self._call_fut,
            request=None, permission=PERM_ADMIN_SITE, context=project)

    def test_view_permission_on_public_project_for_anonymous(self):
        from yait.auth import PERM_VIEW_PROJECT
        request = self._make_request()
        project = self._make_project(public=True)
        self.assert_(self._call_fut(request, PERM_VIEW_PROJECT, project))

    def test_non_view_permission_on_public_project_for_anonymous(self):
        from yait.auth import PERM_MANAGE_PROJECT
        request = self._make_request()
        project = self._make_project(public=True)
        self.assert_(not self._call_fut(request, PERM_MANAGE_PROJECT, project))

    def test_view_permission_on_private_project_for_anonymous(self):
        from yait.auth import PERM_VIEW_PROJECT
        request = self._make_request()
        project = self._make_project()
        self.assert_(not self._call_fut(request, PERM_VIEW_PROJECT, project))

    def test_site_permission_for_site_admin(self):
        from yait.auth import PERM_ADMIN_SITE
        login = u'admin'
        self._make_user(login, is_admin=True)
        request = self._make_request(user=login)
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))

    def _test_role(self, login, project, expected):
        # An helper method for all 'test_role_*()' below
        from yait.auth import PERM_MANAGE_PROJECT
        from yait.auth import PERM_PARTICIPATE_IN_PROJECT
        from yait.auth import PERM_SEE_PRIVATE_TIMING_INFO
        from yait.auth import PERM_VIEW_PROJECT
        missing_perms = set(
            ['view', 'participate', 'see_timing', 'manage_project']
            ).difference(expected.keys())
        assert not missing_perms, \
            'The following permissions are not tested: %s' % missing_perms
        request = self._make_request(user=login)
        for key, permission in {
            'view': PERM_VIEW_PROJECT,
            'participate': PERM_PARTICIPATE_IN_PROJECT,
            'see_timing': PERM_SEE_PRIVATE_TIMING_INFO,
            'manage_project': PERM_MANAGE_PROJECT}.items():
            allowed = expected[key]
            self.assertEqual(
                self._call_fut(request, permission, project), allowed)

    def test_role_site_admin(self):
        project = self._make_project()
        login = u'admin'
        self._make_user(login, is_admin=True)
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'manage_project': True}
        self._test_role(login, project, expected)

    def test_role_project_admin(self):
        from yait.auth import ROLE_PROJECT_MANAGER
        project = self._make_project()
        login = u'project_admin'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'manage_project': True}
        self._test_role(login, project, expected)

    def test_role_project_internal_participant(self):
        from yait.auth import ROLE_PROJECT_INTERNAL_PARTICIPANT
        project = self._make_project()
        login = u'internal_participant'
        self._make_user(login, roles={
                project: ROLE_PROJECT_INTERNAL_PARTICIPANT})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': True,
                    'manage_project': False}
        self._test_role(login, project, expected)

    def test_role_project_participant(self):
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        project = self._make_project()
        login = u'participant'
        self._make_user(login, roles={project: ROLE_PROJECT_PARTICIPANT})
        expected = {'view': True,
                    'participate': True,
                    'see_timing': False,
                    'manage_project': False}
        self._test_role(login, project, expected)

    def test_role_project_viewer(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        project = self._make_project()
        login = u'project_viewer'
        self._make_user(login, roles={project: ROLE_PROJECT_VIEWER})
        expected = {'view': True,
                    'participate': False,
                    'see_timing': False,
                    'manage_project': False}
        self._test_role(login, project, expected)

    def test_no_role(self):
        project = self._make_project()
        login = u'no_role'
        self._make_user(login)
        expected = {'view': False,
                    'participate': False,
                    'see_timing': False,
                    'manage_project': False}
        self._test_role(login, project, expected)

    def test_role_in_another_project(self):
        from yait.auth import PERM_MANAGE_PROJECT
        project1 = self._make_project(name=u'p1')
        project2 = self._make_project(name=u'p2')
        login = u'user1'
        # give role in project 1
        self._make_user(login, roles={project1: PERM_MANAGE_PROJECT})
        # but check in project 2
        expected = {'view': False,
                    'participate': False,
                    'see_timing': False,
                    'manage_project': False}
        self._test_role(login, project2, expected)

    def test_cache_site_permissions(self):
        from yait.auth import PERM_ADMIN_SITE
        login = u'admin'
        admin = self._make_user(login, is_admin=True)
        request = self._make_request(login)
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))
        admin.is_admin = False
        self.session.flush()
        self.assert_(self._call_fut(request, PERM_ADMIN_SITE))

    def test_cache_project_permissions(self):
        from yait.models import Role
        from yait.auth import PERM_MANAGE_PROJECT
        from yait.auth import ROLE_PROJECT_MANAGER
        project = self._make_project()
        login = u'user1'
        self._make_user(login, roles={project: ROLE_PROJECT_MANAGER})
        request = self._make_request(user=login)
        self.assert_(self._call_fut(request, PERM_MANAGE_PROJECT, project))
        role = self.session.query(Role).one()
        self.session.delete(role)
        self.assert_(self._call_fut(request, PERM_MANAGE_PROJECT, project))
