"""Test the ``run`` module.

$Id$
"""

from unittest import TestCase


class TestApp(TestCase):

    def test_app(self):
        ## This test looks dull but it actually checks that we have no
        ## error in the 'cofigure.zcml'.
        from repoze.bfg.router import Router
        from yait.run import app
        global_settings = {}
        settings = dict(db_string='sqlite://')
        wsgi_app = app(global_settings, **settings)
        self.assert_(isinstance(wsgi_app, Router))
