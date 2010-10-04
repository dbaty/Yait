"""Test views related to issues.

$Id$
"""

from unittest import TestCase

from yait.tests.base import TestCaseForViews


class TestIssueAddForm(TestCaseForViews):

    template_under_test = 'templates/issue_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import add_issue_form
        return add_issue_form(*args, **kwargs)

    def test_add_issue_form_unknown_project(self):
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_add_issue_form_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_form_allow_participant(self):
        from yait.forms import AddIssueForm
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        renderer = self._makeRenderer()
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        self._callFUT(context, request)
        form = renderer._received.get('form', None)
        self.assert_(isinstance(form, AddIssueForm))


class TestAddIssue(TestCaseForViews):

    template_under_test = 'templates/issue_add_form.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import add_issue
        return add_issue(*args, **kwargs)

    def test_add_issue_unknown_project(self):
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_add_issue_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel()
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_invalid_form(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        context = self._makeModel()
        post = {'title': u'Issue title', 'text': u''}
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id, post=post,
                                    matchdict=matchdict)
        renderer = self._makeRenderer()
        self._callFUT(context, request)
        self.assertEqual(
            renderer._received.get('form').errors.keys(), ['text'])
        self.assertEqual(len(p.issues), 0)

    def test_add_issue_allow_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        context = self._makeModel()
        post = {'title': u'Issue title', 'text': u'Issue body'}
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id, post=post,
                                    matchdict=matchdict)
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

        context = self._makeModel()
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._callFUT(context, request)
        self.assertEqual(p1.issues[0].ref, 1)

        context = self._makeModel()
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p2'}
        request = self._makeRequest(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._callFUT(context, request)
        self.assertEqual(p2.issues[0].ref, 1)

        ## We need to detach 'p1' from the session, otherwise
        ## SQLAlchemy does not retrieve issues again when we access
        ## 'p1.issues'.
        self.session.expunge(p1)
        p1 = self.session.query(Project).filter_by(name=u'p1').one()
        context = self._makeModel()
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._makeRequest(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._callFUT(context, request)
        self.assertEqual(p1.issues[1].ref, 2)


class TestViewIssue(TestCaseForViews):

    template_under_test = 'templates/issue_view.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import issue_view
        return issue_view(*args, **kwargs)

    def test_issue_view_unknown_project(self):
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_view_reject_not_participant(self):
        self._makeProject(name=u'p1')
        user_id = u'user1'
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_view_unknown_issue(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_view_project_viewer(self):
        from yait.forms import AddChangeForm
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        issue = self._makeIssue(project=p)
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        renderer = self._makeRenderer()
        self._callFUT(context, request)
        renderer.assert_(project=p)
        renderer.assert_(issue=issue)
        self.assert_(isinstance(renderer._received.get('form'),
                                AddChangeForm))
        self.assertEqual(renderer._received.get('form').errors, {})


class TestUpdateIssue(TestCaseForViews):

    template_under_test = 'templates/issue_view.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import issue_update
        return issue_update(*args, **kwargs)

    def test_issue_update_unknown_project(self):
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_update_reject_not_viewer(self):
        self._makeProject(name=u'p1')
        user_id = u'user1'
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_update_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_VIEWER})
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_update_unknown_issue(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_update_project_viewer(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._makeProject(name=u'p1')
        issue = self._makeIssue(project=p)
        user_id = u'user1'
        self._makeUser(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        context = self._makeModel()
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        post = {'text': u'comment', 'assignee': u'user2', }
        request = self._makeRequest(user_id=user_id,
                                    matchdict=matchdict,
                                    post=post)
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        location = response.headers['location'].split('?')[0]
        self.assert_(location.endswith('%s/%d' % (p.name, issue.ref)))
        self.assertEqual(len(issue.changes), 1)
        self.assertEqual(issue.assignee, u'user2')
        self.assertEqual(issue.changes[0].changes,
                         {'assignee': (None, u'user2')})


class TestAjaxRenderReST(TestCase):

    def _callFUT(self, *args, **kwargs):
        from yait.views.issue import ajax_render_ReST
        return ajax_render_ReST(*args, **kwargs)

    def _makeRequest(self, params=None):
        from repoze.bfg.testing import DummyRequest
        return DummyRequest(params=params)

    def test_ajax_render_rest(self):
        self.assertEqual(
            self._callFUT(None, self._makeRequest({'text': '**bold**'})),
            {'rendered': '<p><strong>bold</strong></p>'})

    def test_ajax_render_rest_empty_text(self):
        self.assertEqual(self._callFUT(None, self._makeRequest()),
                         {'rendered': ''})

