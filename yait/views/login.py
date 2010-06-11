"""Login, post-login and logout views.

$Id$
"""

from urllib import quote_plus

from webob.exc import HTTPFound
from repoze.bfg.chameleon_zpt import render_template_to_response

from yait.views.utils import TemplateAPI


def login_form(context, request):
    api = TemplateAPI(context, request)
    came_from = request.params.get('came_from') or api.referrer or '/'
    login_counter = request.environ.get('repoze.who.logins', 0)
    error_msg = None
    if login_counter != 0:
        error_msg = 'Wrong user name or password.'
    return render_template_to_response('templates/login.pt',
                                       api=api,
                                       came_from=came_from,
                                       error_msg=error_msg,
                                       login_counter=login_counter)


def post_login(request):
    identity = request.environ.get('repoze.who.identity')
    came_from = request.params.get('came_from', '') or '/'
    if identity:
        destination = came_from
    else:
        login_counter = request.environ['repoze.who.logins'] + 1
        came_from = quote_plus(came_from)
        destination = '/login_form?came_from=%s&__logins=%s' % (
            came_from, login_counter)
    return HTTPFound(location=destination)


def post_logout(request):
    url = '%s?status_message=%s' % (
        request.application_url,
        quote_plus(u'You have been logged out.'))
    return HTTPFound(location=url)
