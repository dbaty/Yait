"""Base utilities and classes for our tests.

$Id$
"""

from unittest import TestCase


def get_testing_db_session():
    from yait.models import DBSession
    from yait.models import initialize_sql
    initialize_sql('sqlite://')
    return DBSession


class TestCaseForViews(TestCase):

    def setUp(self):
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        ## We need to register these templates since they are used in
        ## TemplateAPI which is in turn used in almost all views.
        self.config.testing_add_template('templates/form_macros.pt')
        self.config.testing_add_template('templates/master.pt')
        self.config.begin()
        self.session = get_testing_db_session()

    def tearDown(self):
        self.config.end()
        self.session.remove()

    def _makeRenderer(self):
        from repoze.bfg.testing import registerTemplateRenderer
        return registerTemplateRenderer(self.template_under_test)

    def _makeModel(self):
        from repoze.bfg.testing import DummyModel
        return DummyModel()

    def _makeRequest(self, user_id=None):
        from repoze.bfg.testing import DummyRequest
        environ = {}
        if user_id is not None:
            environ['repoze.who.identity'] = dict(uid=user_id)
        return DummyRequest(environ=environ)

    def _makeSiteAdmin(self, user_id):
        from yait.models import Admin
        self.session.add(Admin(user_id=user_id))

    def _makeUser(self, user_id, roles=None):
        from yait.models import Role
        if roles is None:
            roles = {}
        for project, role in roles.items():
            r = Role(user_id=user_id, project_id=project.id, role=role)
            self.session.add(r)

    def _makeProject(self, name=u'name', title=u'title', public=False):
        from yait.models import Project
        p = Project(name=name, title=title, public=public)
        self.session.add(p)
        self.session.flush() # need to flush to have an id later
        return p
