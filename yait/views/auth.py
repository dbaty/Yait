"""Login, logout and forbidden views.

Policies are defined in the 'yait.auth' module, not here.
"""

from urllib import quote_plus

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember

from yait.auth import check_password
from yait.i18n import _
from yait.views.utils import TemplateAPI


def login_form(request, login_failed=False):
    next = request.GET.get('next') or request.POST.get('next') or \
        request.route_url('home')
    api = TemplateAPI(request, _(u'Log in'))
    api.show_login_link = False
    bindings = {'api': api,
                'next': next,
                'login_failed': login_failed,
                'needs_login': 'needs_login' in request.GET}
    return render_to_response('../templates/login.pt', bindings)


def login(request, _check_password=check_password, _remember=remember):
    """Login user if the credentials match or return the login form.

    ``_check_password`` and ``remember`` are only customized in tests.
    """
    next = request.GET.get('next') or \
        request.POST.get('next') or \
        quote_plus(request.get('HTTP_REFERER') or request.route_url('home'))
    login = request.POST.get('login', '')
    password = request.POST.get('password', '')
    user = _check_password(login, password)
    if user is None:
        return login_form(request, login_failed=True)
    headers = _remember(request, user.id)
    return HTTPSeeOther(location=next, headers=headers)


def logout(request, _forget=forget):
    """Logout the user.

    ``_forget`` is only customized in tests.
    """
    headers = _forget(request)
    msg = _(u'You have been successfully logged out.')
    request.session.flash(msg, 'success')
    return HTTPSeeOther(location=request.application_url, headers=headers)


def forbidden(request):
    if not authenticated_userid(request):
        url = request.route_url('login',
                                _query={'next': request.url,
                                        'needs_login': '1'})
        return HTTPSeeOther(location=url)
    # User is logged in but is not allowed to do what she tried.
    bindings = {'api': TemplateAPI(request),
                'forbidden_url': request.url}
    return render_to_response('../templates/forbidden.pt', bindings)
