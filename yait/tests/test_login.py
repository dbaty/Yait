"""Test login/logout related views."""


from yait.tests.base import TestCaseForViews


class TestLoginViews(TestCaseForViews):

    template_under_test = '../templates/login.pt'

    def _call_fut(self, request):
        from yait.views.login import login_form
        return login_form(request)

    def test_login_form_first_display(self):
        renderer = self._make_renderer()
        request = self._make_request()
        self._call_fut(request)
        renderer.assert_(login_counter=0)
        renderer.assert_(error_msg=None)

    def test_login_form_second_display(self):
        renderer = self._make_renderer()
        environ = {'repoze.who.logins': 1}
        request = self._make_request(environ=environ)
        self._call_fut(request)
        renderer.assert_(login_counter=1)
        renderer.assert_(error_msg=u'Wrong user name or password.')

class TestPostLoginViews(TestCaseForViews):

    template_under_test = '../templates/login.pt'

    def _call_fut(self, request):
        from yait.views.login import post_login
        return post_login(request)

    def test_post_login_try_logged_in(self):
        post = {'next': 'http://came.from'}
        environ = {'repoze.who.identity': 'jsmith'}
        request = self._make_request(post=post, environ=environ)
        response = self._call_fut(request)
        self.assertEqual(response.status, '302 Found')
        self.assertEqual(response.location, 'http://came.from')

    def test_post_login_try_not_logged_in(self):
        post = {'next': 'http://came.from'}
        environ = {'repoze.who.logins': 123}
        request = self._make_request(post=post, environ=environ)
        response = self._call_fut(request)
        self.assertEqual(response.status, '302 Found')
        self.assertIn('login_form', response.location)
        self.assertIn('&__logins=124', response.location)


class TestPostLogoutViews(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.login import post_logout
        return post_logout(request)

    def test_post_logout(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '302 Found')        
        self.assertIn('status_message', response.location)
