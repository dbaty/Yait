"""Test the ``app`` module."""


from unittest import TestCase


class TestApp(TestCase):

    def test_make_app(self):
        from pyramid.router import Router
        from yait.app import make_app
        global_settings = {}
        settings = {'yait.db_url': 'sqlite://'}
        wsgi_app = make_app(global_settings, **settings)
        self.assertIsInstance(wsgi_app, Router)
