from pyramid.decorator import reify
from pyramid.renderers import get_renderer

from yait.models import DBSession
from yait.models import Project
from yait.models import Role


HTML_TITLE = u'Yait'


class ActionBar:
    """Define reified properties used in the action bar.

    It is expected to be used as a mix-in class by ``TemplateAPI``.
    """

    @reify
    def all_projects(self):
        """Return all projects that the current user has access to."""
        user = self.request.user
        session = DBSession()
        if user.is_admin:
            projects = session.query(Project)
        elif user.id:
            public = session.query(Project).filter_by(public=True)
            has_role = session.query(Project).join(Role).filter(
                Project.id == Role.project_id)
            projects = has_role.union(public)
        else:
            projects = session.query(Project).filter_by(public=True)
        return projects.order_by(Project.title).all()


class TemplateAPI(object, ActionBar):
    """Provide a master template and various information and utilities
    that can be used in any template.
    """

    def __init__(self, request, html_title=''):
        self.request = request
        self.layout = get_renderer('../templates/layout.pt').implementation()
        if html_title:
            self.html_title = u'Yait - %s' % html_title
        else:
            self.html_title = u'Yait'
        self.notifications = {
            'success': self.request.session.pop_flash('success'),
            'error': self.request.session.pop_flash('error')}
        self.logged_in = request.user.id is not None
        self.show_login_link = not self.logged_in
        self.is_admin = request.user.is_admin
        self.cache = request.cache

    @reify
    def form_macros(self):
        return get_renderer(
            '../templates/form_macros.pt').implementation().macros

    def route_url(self, route_name, *elements, **kw):
        return self.request.route_url(route_name, *elements, **kw)

    def static_url(self, path, **kw):
        if ':' not in path:
            path = 'yait:%s' % path
        return self.request.static_url(path, **kw)
