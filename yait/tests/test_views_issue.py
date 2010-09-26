"""Test views related to issues.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestIssueAddForm(TestCaseForViews):

    template_under_test = 'templates/issue_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import add_issue_form
        return add_issue_form(*args, **kwargs)

    def test_add_issue_form_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel(project_name=u'p1')
        request = self._makeRequest(user_id=user_id)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_form_allow_participant(self):
        from yait.forms import AddIssueForm
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        renderer = self._makeRenderer()
        context = self._makeModel(project_name=u'p1')
        request = self._makeRequest(user_id=user_id)
        self._callFUT(context, request)
        form = renderer._received.get('form', None)
        self.assert_(isinstance(form, AddIssueForm))


class TestAddIssue(TestCaseForViews):

    template_under_test = 'templates/issue_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import add_issue
        return add_issue(*args, **kwargs)

    def test_add_issue_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel(project_name=u'p1')
        request = self._makeRequest(user_id=user_id)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_allow_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        context = self._makeModel(project_name=u'p1')
        post = dict(title=u'Issue title', text=u'Issue body')
        request = self._makeRequest(user_id=user_id, post=post)
        response = self._callFUT(context, request)
        location = response.headers['location']
        self.assert_(location.endswith('%s/1' % p.name))
        self.assertEqual(len(p.issues), 1)
        issue = p.issues[0]
        self.assertEqual(issue.title, u'Issue title')
        self.assertEqual(issue.reporter, user_id)
        self.assertEqual(issue.ref, 1)
        self.assertEqual(len(issue.changes), 1)
        change = issue.changes[0]
        self.assertEqual(change.text, u'Issue body')
        self.assertEqual(change.author, user_id)
        self.assertEqual(change.changes, {})

    def test_add_issue_check_references(self):
        from yait.models import Project
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p1 = self._makeProject(name=u'p1')
        p2 = self._makeProject(name=u'p2')
        user_id = u'user1'
        self._makeUser(user_id, roles={p1: ROLE_PROJECT_PARTICIPANT,
                                       p2: ROLE_PROJECT_PARTICIPANT})

        context = self._makeModel(project_name=u'p1')
        post = dict(title=u't', text=u't')
        request = self._makeRequest(user_id=user_id, post=post)
        self._callFUT(context, request)
        self.assertEqual(p1.issues[0].ref, 1)

        context = self._makeModel(project_name=u'p2')
        post = dict(title=u't', text=u't')
        request = self._makeRequest(user_id=user_id, post=post)
        self._callFUT(context, request)
        self.assertEqual(p2.issues[0].ref, 1)

        ## We need to detach 'p1' from the session, otherwise
        ## SQLAlchemy does not retrieve issues again when we access
        ## 'p1.issues'.
        self.session.expunge(p1)
        p1 = self.session.query(Project).filter_by(name=u'p1').one()
        context = self._makeModel(project_name=u'p1')
        post = dict(title=u't', text=u't')
        request = self._makeRequest(user_id=user_id, post=post)
        self._callFUT(context, request)
        self.assertEqual(p1.issues[1].ref, 2)
