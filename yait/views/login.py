"""Login, post-login and logout views.

$Id$
"""

from urllib import quote_plus

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

from yait.views.utils import TemplateAPI


# FIXME: to be reviewed. Check that using repoze.who is really useful.
# FIXME: use HTTPSeeOther instead of HTTPFound

def login_form(request):
    api = TemplateAPI(request)
    next = request.GET.get('next') or \
        request.POST.get('next') or \
        quote_plus(api.referrer or api.app_url)
    login_counter = request.environ.get('repoze.who.logins', 0)
    error_msg = None
    if login_counter != 0:
        error_msg = 'Wrong user name or password.'
    return render_to_response('../templates/login.pt',
                              {'api': api,
                               'next': next,
                               'error_msg': error_msg,
                               'login_counter': login_counter})


def post_login(request):
    identity = request.environ.get('repoze.who.identity')
    next = request.POST.get('next', '') or request.application_url
    if identity:
        destination = next
    else:
        login_counter = request.environ['repoze.who.logins'] + 1
        next = quote_plus(next)
        destination = '/login_form?next=%s&__logins=%s' % (
            next, login_counter)
    return HTTPFound(location=destination)


def post_logout(request):
    url = '%s?status_message=%s' % (
        request.application_url,
        quote_plus(u'You have been logged out.'))
    return HTTPFound(location=url)
