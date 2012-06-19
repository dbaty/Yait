from yait.tests.base import TestCaseForViews


class DummyCallable(object):
    def __init__(self, res=None):
        self.called = []
        self.res = res

    def __call__(self, *args, **kwargs):
        self.called.append((args, kwargs))
        return self.res


class TestLoginForm(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.auth import login_form
        return login_form(request)

    def test_login_form(self):
        request = self._make_request(get={'next': '/foo'})
        res = self._call_fut(request)
        self.assertEqual(res['login_failed'], False)
        self.assertEqual(res['needs_login'], False)
        self.assertEqual(res['next'], '/foo')
        self.assertEqual(res['api'].show_login_link, False)

    def test_login_form_after_forbidden_when_anonymous(self):
        next = '/restricted'
        request = self._make_request(get={'needs_login': '1',
                                          'next': next})
        res = self._call_fut(request)
        self.assertEqual(res['needs_login'], True)
        self.assertEqual(res['next'], next)


class TestLogin(TestCaseForViews):

    def _call_fut(self, request, _remember, _check_password):
        from yait.views.auth import login
        return login(request, _check_password, _remember)

    def test_login_success(self):
        class DummyUser(object):
            id = 1
        next = '/go-to'
        post = {'next': next}
        request = self._make_request(post=post)
        remember = DummyCallable()
        check_password = DummyCallable(DummyUser())
        response = self._call_fut(request, remember, check_password)
        self.assertEqual(response.status, '303 See Other')
        self.assertEqual(response.location, next)
        self.assertEqual(len(remember.called), 1)

    def test_login_failure(self):
        post = {'next': '/go-to'}
        request = self._make_request(post=post)
        remember = DummyCallable()
        check_password = DummyCallable(None)
        res = self._call_fut(request, remember, check_password)
        self.assertEqual(res['login_failed'], True)
        self.assertEqual(len(remember.called), 0)


class TestLogout(TestCaseForViews):

    def _call_fut(self, request, _forget):
        from yait.views.auth import logout
        return logout(request, _forget)

    def test_basics(self):
        forget = DummyCallable()
        request = self._make_request()
        request.application_url = '/home'
        response = self._call_fut(request, forget)
        self.assertEqual(response.status, '303 See Other')
        self.assertEqual(response.location, request.application_url)
        self.assertEqual(len(forget.called), 1)


class TestForbidden(TestCaseForViews):

    def _call_fut(self, request):
        from yait.views.auth import forbidden
        return forbidden(request)

    def test_not_logged_in_show_login_form(self):
        request = self._make_request()
        response = self._call_fut(request)
        self.assertEqual(response.status, '303 See Other')
        self.assertIn('login', response.location)

    def test_logged_in_return_forbidden(self):
        login = u'user1'
        self._make_user(login)
        request = self._make_request(user=login)
        request.url = '/forbidden'
        res = self._call_fut(request)
        self.assertEqual(res['forbidden_url'], request.url)
