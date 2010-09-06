"""Test the ``run`` module.

$Id$
"""

from unittest import TestCase


class TestApp(TestCase):

    def test_app(self):
        from repoze.bfg.router import Router
        from yait.run import app
        global_settings = {}
        wsgi_app = app(global_settings)
        self.assert_(isinstance(wsgi_app, Router))
