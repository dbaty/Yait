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
        ## FIXME: could be replaced by return self.config.testing_add_template(self.template_under_test)
        from repoze.bfg.testing import registerTemplateRenderer
        return registerTemplateRenderer(self.template_under_test)

    def _makeModel(self, *args, **kwargs):
        from repoze.bfg.testing import DummyModel
        return DummyModel(*args, **kwargs)

    def _makeRequest(self, user_id=None, post=None, environ=None,
                     matchdict=None):
        from repoze.bfg.testing import DummyRequest
        if environ is None:
            environ = {}
        if user_id is not None:
            environ['repoze.who.identity'] = {'uid': user_id}
        if post is not None:
            from webob.multidict import MultiDict
            post = MultiDict(post)
        request = DummyRequest(environ=environ, post=post)
        if matchdict is not None:
            request.matchdict = matchdict
        return request

    def _makeSiteAdmin(self, user_id):
        from yait.models import Admin
        a = Admin(user_id=user_id)
        self.session.add(a)
        return a

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
