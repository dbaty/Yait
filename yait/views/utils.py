from pyramid.renderers import get_renderer


HTML_TITLE = u'Yait'


class TemplateAPI(object):
    """Provide a master template and various information and utilities
    that can be used in any template.
    """
    def __init__(self, request, html_title=''):
        self.request = request
        self.layout = get_renderer('../templates/layout.pt').implementation()
        self.form_macros = get_renderer(
            '../templates/form_macros.pt').implementation().macros
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

    def route_url(self, route_name, *elements, **kw):
        return self.request.route_url(route_name, *elements, **kw)

    def static_url(self, path, **kw):
        if ':' not in path:
            path = 'yait:%s' % path
        return self.request.static_url(path, **kw)
