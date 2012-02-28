from unittest import TestCase

from yait.tests.base import TestCaseForViews


class TestIssueAddForm(TestCaseForViews):

    template_under_test = '../templates/issue_add.pt'

    def _call_fut(self, request):
        from yait.views.issue import add_form
        return add_form(request)

    def test_add_issue_form_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_add_issue_form_reject_not_participant(self):
        from pyramid.httpexceptions import HTTPForbidden
        from yait.auth import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_issue_form_allow_participant(self):
        from yait.forms import AddIssueForm
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_PARTICIPANT})
        renderer = self._make_renderer()
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self._call_fut(request)
        self.assertIsInstance(renderer.form, AddIssueForm)


class TestAddIssue(TestCaseForViews):

    template_under_test = '../templates/issue_add.pt'

    def _call_fut(self, request):
        from yait.views.issue import add
        return add(request)

    def test_add_issue_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'p1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_add_issue_reject_not_participant(self):
        from pyramid.httpexceptions import HTTPForbidden
        from yait.auth import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_add_issue_invalid_form(self):
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_PARTICIPANT})
        post = {'title': u'Issue title', 'text': u''}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, post=post,
                                    matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        self.assertEqual(renderer.form.errors.keys(), ['text'])
        self.assertEqual(len(p.issues), 0)

    def test_add_issue_allow_participant(self):
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        login = u'user1'
        user = self._make_user(login, roles={p: ROLE_PROJECT_PARTICIPANT})
        post = {'title': u'Issue title', 'text': u'Issue body'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, post=post,
                                     matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(len(p.issues), 1)
        issue = p.issues[0]
        self.assertEqual(issue.title, u'Issue title')
        self.assertEqual(issue.reporter, user.id)
        self.assertEqual(issue.ref, 1)
        self.assertEqual(len(issue.changes), 1)
        change = issue.changes[0]
        self.assertEqual(change.text, u'Issue body')
        self.assertEqual(change.author, user.id)
        self.assertEqual(change.changes, {})

    def test_add_issue_check_references(self):
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        from yait.models import Project
        p1 = self._make_project(name=u'p1')
        p2 = self._make_project(name=u'p2')
        login = u'user1'
        self._make_user(login, roles={p1: ROLE_PROJECT_PARTICIPANT,
                                      p2: ROLE_PROJECT_PARTICIPANT})
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, post=post,
                                     matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p1.issues[0].ref, 1)

        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p2'}
        request = self._make_request(user=login, post=post,
                                     matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p2.issues[0].ref, 1)

        # We need to detach 'p1' from the session, otherwise
        # SQLAlchemy does not retrieve issues again when we access
        # 'p1.issues'.
        self.session.expunge(p1)
        p1 = self.session.query(Project).filter_by(name=u'p1').one()
        post = {'title': u't', 'text': u't'}
        matchdict = {'project_name': u'p1'}
        request = self._make_request(user=login, post=post,
                                     matchdict=matchdict)
        self._call_fut(request)
        self.assertEqual(p1.issues[1].ref, 2)


class TestViewIssue(TestCaseForViews):

    template_under_test = '../templates/issue.pt'

    def _call_fut(self, request):
        from yait.views.issue import view
        return view(request)

    def test_issue_ref_not_an_integer(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'p1', 'issue_ref': u'not an int'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_issue_view_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_issue_view_reject_not_participant(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login)
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_issue_view_unknown_issue(self):
        from pyramid.httpexceptions import HTTPNotFound
        from yait.auth import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_issue_view_project_viewer(self):
        from yait.auth import ROLE_PROJECT_VIEWER
        from yait.forms import AddChangeForm
        p = self._make_project(name=u'p1')
        issue = self._make_issue(project=p)
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        request = self._make_request(user=login, matchdict=matchdict)
        renderer = self._make_renderer()
        self._call_fut(request)
        renderer.assert_(project=p)
        renderer.assert_(issue=issue)
        self.assertIsInstance(renderer.form, AddChangeForm)
        self.assertEqual(renderer.form.errors, {})


class TestUpdateIssue(TestCaseForViews):

    template_under_test = '../templates/issue.pt'

    def _call_fut(self, request):
        from yait.views.issue import update
        return update(request)

    def test_issue_update_unknown_project(self):
        from pyramid.httpexceptions import HTTPNotFound
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_issue_update_reject_not_viewer(self):
        from pyramid.httpexceptions import HTTPForbidden
        self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login)
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_issue_update_reject_not_participant(self):
        from pyramid.httpexceptions import HTTPForbidden
        from yait.auth import ROLE_PROJECT_VIEWER
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_VIEWER})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPForbidden, self._call_fut, request)

    def test_issue_update_unknown_issue(self):
        from pyramid.httpexceptions import HTTPNotFound
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_PARTICIPANT})
        matchdict = {'project_name': u'p1', 'issue_ref': u'1'}
        request = self._make_request(user=login, matchdict=matchdict)
        self.assertRaises(HTTPNotFound, self._call_fut, request)

    def test_issue_update_project_viewer(self):
        from yait.auth import ROLE_PROJECT_PARTICIPANT
        p = self._make_project(name=u'p1')
        issue = self._make_issue(project=p)
        login = u'user1'
        self._make_user(login, roles={p: ROLE_PROJECT_PARTICIPANT})
        matchdict = {'project_name': u'p1', 'issue_ref': str(issue.ref)}
        post = {'text': u'comment', 'assignee': u'user2', }
        request = self._make_request(user=login, matchdict=matchdict,
                                     post=post)
        self._call_fut(request)
        self.assertEqual(len(issue.changes), 1)
        self.assertEqual(issue.assignee, u'user2')
        self.assertEqual(issue.changes[0].changes,
                         {'assignee': (None, u'user2')})


class TestAjaxRenderReST(TestCase):

    def _call_fut(self, request):
        from yait.views.issue import ajax_render_text
        return ajax_render_text(request)

    def _make_request(self, get=None):
        from pyramid.testing import DummyRequest
        return DummyRequest(params=get)

    def test_ajax_render_rest(self):
        request = self._make_request(get={'text': '**bold**',
                                          'text_renderer': 'rest'})
        self.assertEqual(
            self._call_fut(request),
            {'rendered': '<p><strong>bold</strong></p>'})

    def test_ajax_render_rest_empty_text(self):
        request = self._make_request(get={'text': '',
                                          'text_renderer': 'rest'})
        self.assertEqual(self._call_fut(request), {'rendered': ''})
