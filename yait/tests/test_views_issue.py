"""Test views related to issues."""


from unittest import TestCase

from yait.tests.base import TestCaseForViews


class TestIssueAddForm(TestCaseForViews):

    template_under_test = '../templates/issue_add.pt'

    def _call_fut(self, request):
        from yait.views.issue import add_issue_form
        return add_issue_form(request)

    def test_add_issue_form_unknown_project(self):
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_add_issue_form_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_form_allow_participant(self):
        from yait.forms import AddIssueForm
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        renderer = self._make_renderer()
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        self._call_fut(request)
        form = renderer._received.get('form', None)
        self.assertIsInstance(form, AddIssueForm)


class TestAddIssue(TestCaseForViews):

    template_under_test = '../templates/issue_add.pt'

    def _call_fut(self, request):
        from yait.views.issue import add_issue
        return add_issue(request)

    def test_add_issue_unknown_project(self):
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_add_issue_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_add_issue_invalid_form(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        post = {'title': u'Issue title', 'text': u''}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id, post=post,
                                    matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(
            renderer._received.get('form').errors.keys(), ['text'])
        self.assertEqual(len(p.issues), 0)

    def test_add_issue_allow_participant(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        post = {'title': u'Issue title', 'text': u'Issue body'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id, post=post,
                                    matchdict=matchdict)
        response = self._call_fut(request)
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
        p1 = self._make_project(name=u'p1')
        p2 = self._make_project(name=u'p2')
        user_id = u'user1'
        self._make_user(user_id, roles={p1: ROLE_PROJECT_PARTICIPANT,
                                        p2: ROLE_PROJECT_PARTICIPANT})

        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p1.issues[0].ref, 1)

        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p2'}
        request = self._make_request(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p2.issues[0].ref, 1)

        ## We need to detach 'p1' from the session, otherwise
        ## SQLAlchemy does not retrieve issues again when we access
        ## 'p1.issues'.
        self.session.expunge(p1)
        p1 = self.session.query(Project).filter_by(name=u'p1').one()
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user_id=user_id, post=post,
                                    matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p1.issues[1].ref, 2)


class TestViewIssue(TestCaseForViews):

    template_under_test = '../templates/issue.pt'

    def _call_fut(self, request):
        from yait.views.issue import issue_view
        return issue_view(request)

    def test_issue_view_unknown_project(self):
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_view_reject_not_participant(self):
        self._make_project(name=u'p1')
        user_id = u'user1'
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_view_unknown_issue(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_view_project_viewer(self):
        from yait.forms import AddChangeForm
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        issue = self._make_issue(project=p)
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        renderer.assert_(project=p)
        renderer.assert_(issue=issue)
        self.assertIsInstance(renderer._received.get('form'),
                              AddChangeForm)
        self.assertEqual(renderer._received.get('form').errors, {})


class TestUpdateIssue(TestCaseForViews):

    template_under_test = '../templates/issue.pt'

    def _call_fut(self, request):
        from yait.views.issue import issue_update
        return issue_update(request)

    def test_issue_update_unknown_project(self):
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_update_reject_not_viewer(self):
        self._make_project(name=u'p1')
        user_id = u'user1'
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_update_reject_not_participant(self):
        from yait.views.utils import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '401 Unauthorized')

    def test_issue_update_unknown_issue(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict)
        response = self._call_fut(request)
        self.assertEqual(response.status, '404 Not Found')

    def test_issue_update_project_viewer(self):
        from yait.views.utils import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        issue = self._make_issue(project=p)
        user_id = u'user1'
        self._make_user(user_id, roles={p: ROLE_PROJECT_PARTICIPANT})
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        post = {'text': u'comment', 'assignee': u'user2', }
        request = self._make_request(user_id=user_id,
                                    matchdict=matchdict,
                                    post=post)
        response = self._call_fut(request)
        self.assertEqual(response.status, '302 Found')
        location = response.headers['location'].split('?')[0]
        self.assert_(location.endswith('%s/%d' % (p.name, issue.ref)))
        self.assertEqual(len(issue.changes), 1)
        self.assertEqual(issue.assignee, u'user2')
        self.assertEqual(issue.changes[0].changes,
                         {'assignee': (None, u'user2')})


class TestAjaxRenderReST(TestCase):

    def _call_fut(self, request):
        from yait.views.issue import ajax_render_text
        return ajax_render_text(request)

    def _make_request(self, post=None):
        from pyramid.testing import DummyRequest
        return DummyRequest(post=post)

    def test_ajax_render_rest(self):
        request = self._make_request(post={'text': '**bold**',
                                           'renderer_name': 'rest'})
        self.assertEqual(
            self._call_fut(request),
            {'rendered': '<p><strong>bold</strong></p>'})

    def test_ajax_render_rest_empty_text(self):
        request = self._make_request(post={'text': '',
                                           'renderer_name': 'rest'})
        self.assertEqual(self._call_fut(request), {'rendered': ''})
