"""Login, post-login and logout views.

$Id$
"""

from urllib import quote_plus

from webob.exc import HTTPFound

from repoze.bfg.renderers import render_to_response

from yait.views.utils import TemplateAPI


def login_form(context, request):
    api = TemplateAPI(context, request)
    came_from = request.params.get('came_from') or api.referrer or '/'
    login_counter = request.environ.get('repoze.who.logins', 0)
    error_msg = None
    if login_counter != 0:
        error_msg = 'Wrong user name or password.'
    return render_to_response('templates/login.pt',
                              dict(api=api,
                                   came_from=came_from,
                                   error_msg=error_msg,
                                   login_counter=login_counter))


def post_login(context, request): ## FIXME: had only 'request', before
    identity = request.environ.get('repoze.who.identity')
    came_from = request.POST.get('came_from', '') or '/'
    if identity:
        destination = came_from
    else:
        login_counter = request.environ['repoze.who.logins'] + 1
        came_from = quote_plus(came_from)
        destination = '/login_form?came_from=%s&__logins=%s' % (
            came_from, login_counter)
    return HTTPFound(location=destination)


def post_logout(context, request): ## FIXME: had only 'request', before
    url = '%s?status_message=%s' % (
        request.application_url,
        quote_plus(u'You have been logged out.'))
    return HTTPFound(location=url)
