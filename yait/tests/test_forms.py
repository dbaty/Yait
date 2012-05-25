from unittest import TestCase


class TestAddIssueForm(TestCase):

    def setUp(self):
        from yait.tests.base import get_testing_db_session
        self.session = get_testing_db_session()

    def tearDown(self):
        self.session.remove()

    def _make_one(self, project, post=None, **kwargs):
        from yait.forms import make_add_issue_form
        if isinstance(post, dict):
            # test helper
            from webob.multidict import MultiDict
            post = MultiDict(post)
        form = make_add_issue_form(project, self.session, post, **kwargs)
        return form

    def _make_user(self, login, fullname=u'', is_admin=False, roles=None):
        from yait.models import Role
        from yait.models import User
        if roles is None:
            roles = {}
        user = User(login=login, password=u'secret', fullname=fullname,
                    email=u'', is_admin=is_admin)
        self.session.add(user)
        self.session.flush()  # sets id
        for project, role in roles.items():
            r = Role(user_id=user.id, project_id=project.id, role=role)
            self.session.add(r)
        return user

    def _make_project(self, name=u'name', title=u'title', public=False):
        from yait.models import Project
        p = Project(name=name, title=title, public=public)
        self.session.add(p)
        self.session.flush()  # sets id
        return p

    def test_assignee_choices(self):
        from yait.auth import ROLE_PROJECT_INTERNAL_PARTICIPANT
        from yait.auth import ROLE_PROJECT_MANAGER
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        from yait.auth import ROLE_PROJECT_VIEWER
        p1 = self._make_project(u'project1')
        p2 = self._make_project(u'project2')
        self._make_user(u'allowed1', u'Allowed 1',
                        roles={p1: ROLE_PROJECT_MANAGER})
        self._make_user(u'allowed2', u'Allowed 2',
                        roles={p1: ROLE_PROJECT_PARTICIPANT})
        self._make_user(u'allowed3', u'Allowed 3',
                        roles={p1: ROLE_PROJECT_INTERNAL_PARTICIPANT})
        self._make_user(u'forbidden1', u'Forbidden 1',
                        roles={p1: ROLE_PROJECT_VIEWER})
        self._make_user(u'forbidden2', u'Forbidden 2',
                        roles={p2: ROLE_PROJECT_MANAGER})
        self._make_user(u'admin', u'Admin', is_admin=True)
        form = self._make_one(project=p1)
        self.assertEqual(form.assignee.choices,
                         [('', u'Nobody'),
                          (6, u'Admin'),
                          (1, u'Allowed 1'),
                          (2, u'Allowed 2'),
                          (3, u'Allowed 3')])

    def test_assignee_not_required(self):
        project = self._make_project(u'project')
        form = self._make_one(project, post={'assignee': u''})
        # assert that no assignee has been selected
        assert form.data['assignee'] == u''
        form.validate()
        self.assert_('assignee' not in form.errors)


# FIXME: run the same tests (and perhaps additional tests if needed)
# against AddChangeForm, with something like this:
# class TestAddChangeForm(TestAddIssue):
#     def test_something_specific(self): ...
# del TestAddChangeForm.test_that_do_not_apply_to_AddChangeForm
