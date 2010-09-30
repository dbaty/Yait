"""Test login/logout related views.

$Id$
"""

from yait.tests.base import TestCaseForViews


class TestLoginViews(TestCaseForViews):

    template_under_test = 'templates/login.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.login import login_form
        return login_form(*args, **kwargs)

    def test_login_form_first_display(self):
        renderer = self._makeRenderer()
        context = self._makeModel()
        request = self._makeRequest()
        self._callFUT(context, request)
        renderer.assert_(login_counter=0)
        renderer.assert_(error_msg=None)

    def test_login_form_second_display(self):
        renderer = self._makeRenderer()
        context = self._makeModel()
        environ = {'repoze.who.logins': 1}
        request = self._makeRequest(environ=environ)
        self._callFUT(context, request)
        renderer.assert_(login_counter=1)
        renderer.assert_(error_msg=u'Wrong user name or password.')

class TestPostLoginViews(TestCaseForViews):

    template_under_test = 'templates/login.pt'

    def _callFUT(self, *args, **kwargs):
        from yait.views.login import post_login
        return post_login(*args, **kwargs)

    def test_post_login_try_logged_in(self):
        post = {'came_from': 'http://came.from'}
        environ = {'repoze.who.identity': 'jsmith'}
        request = self._makeRequest(post=post, environ=environ)
        context = self._makeModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, 'http://came.from')

    def test_post_login_try_not_logged_in(self):
        post = {'came_from': 'http://came.from'}
        environ = {'repoze.who.logins': 123}
        request = self._makeRequest(post=post, environ=environ)
        context = self._makeModel()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')
        self.assert_('login_form' in response.location)
        self.assert_('&__logins=124' in response.location)


class TestPostLogoutViews(TestCaseForViews):

    def _callFUT(self, *args, **kwargs):
        from yait.views.login import post_logout
        return post_logout(*args, **kwargs)

    def test_post_logout(self):
        context = self._makeModel()
        request = self._makeRequest()
        response = self._callFUT(context, request)
        self.assertEqual(response.status, '302 Found')        
        self.assert_('status_message' in response.location)
