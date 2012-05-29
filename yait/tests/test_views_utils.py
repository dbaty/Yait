from unittest import TestCase

from pyramid import testing


class TestTemplateAPI(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_one(self, request):
        from yait.views.utils import TemplateAPI
        return TemplateAPI(request)

    def _set_request_user(self, request, user_id=None, is_admin=False):
        # 'request.user' is a property that normally uses the
        # authentication policy. Since we do not want to set a policy,
        # we fake the property.
        class FakeUser(object):
            pass
        request.user = FakeUser()
        request.user.id = user_id
        request.user.is_admin = is_admin

    def test_notifications(self):
        request = DummyRequest()
        request.session.flash(u'Success 1!', 'success')
        request.session.flash(u'Success 2!', 'success')
        request.session.flash(u'Error 1!', 'error')
        request.session.flash(u'Error 2!', 'error')
        self._set_request_user(request)
        api = self._make_one(request=request)
        expected = {'success': [u'Success 1!', u'Success 2!'],
                    'error': [u'Error 1!', u'Error 2!']}
        self.assertEqual(api.notifications, expected)

    def test_login_link_for_unauthenticated_user(self):
        request = DummyRequest()
        self._set_request_user(request)
        api = self._make_one(request=request)
        self.assert_(api.show_login_link)

    def test_no_login_link_for_logged_in_user(self):
        request = DummyRequest()
        self._set_request_user(request, user_id=1)
        api = self._make_one(request=request)
        self.assert_(not api.show_login_link)

    def test_request_user_related(self):
        request = DummyRequest()
        self._set_request_user(request, user_id=1, is_admin=True)
        api = self._make_one(request=request)
        self.assert_(api.logged_in)
        self.assert_(api.is_admin)

    def test_route_url(self):
        request = DummyRequest()
        self._set_request_user(request)
        request.route_url = lambda route_name, *elements, **kwargs: (
            route_name, elements, kwargs)
        api = self._make_one(request)
        got = api.route_url('route_name', 'foo', bar=1, baz=2)
        expected = ('route_name', ('foo', ), {'bar': 1, 'baz': 2})
        self.assertEqual(got, expected)

    def test_static_url(self):
        request = DummyRequest()
        self._set_request_user(request)
        request.static_url = lambda path, **kwargs: (path, kwargs)
        api = self._make_one(request)
        got = api.static_url('foo:static/foo', bar=1, baz=2)
        expected = ('foo:static/foo', {'bar': 1, 'baz': 2})
        self.assertEqual(got, expected)

    def test_static_url_implicit_package(self):
        request = DummyRequest()
        self._set_request_user(request)
        request.static_url = lambda path, **kwargs: (path, kwargs)
        api = self._make_one(request)
        got = api.static_url('static/foo', bar=1, baz=2)
        expected = ('yait:static/foo', {'bar': 1, 'baz': 2})
        self.assertEqual(got, expected)


class DummyRequest(testing.DummyRequest):
    cache = 'dummy'
