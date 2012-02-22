"""Authentication- and authorization-related views.

Policies are defined in the 'yait.auth' module, not here.
"""

from urllib import quote_plus


from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import remember

from yait.auth import check_password
from yait.views.utils import TemplateAPI


def login_form(request, login_failed=False):
    next = request.GET.get('next') or request.POST.get('next') or \
        request.route_url('home')
    bindings = {'api': TemplateAPI(request),
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
    # FIXME: add confirmation message
    headers = _forget(request)
    return HTTPSeeOther(location=request.application_url, headers=headers)


def forbidden(request):
    if authenticated_userid(request):
        # FIXME: the intention is good, but we should not try to
        # redirect to 'next' (after login) if this request is a
        # POST. The redirection will be a GET request, which may not
        # match any route (or not the same as the original POST
        # request).
        #
        # Possible solutions:
        #
        # 1. When submitting a form, a quick AJAX call checks whether
        #    the user is still logged in (i.e. if the auth ticket is
        #    still valid), which will have the nice side-effect to
        #    renew the authentication ticket. If it is, the form is
        #    submitted at once. Otherwise, a modal dialog is displayed
        #    requesting the user to log in (which is done through
        #    AJAX).
        #
        # 2. On each page, as soon as the page loads, we set up a
        #    clock. When we are about to reach the auth ticket
        #    timeout, a proheminent message is displayed asking to
        #    login again (through AJAX).
        url = request.route_url('login',
                                _query={'next': request.url,
                                        'needs_login': '1'})
        return HTTPSeeOther(location=url)
    # User is logged in but is not allowed to do what she tried.
    bindings = {'api': TemplateAPI(request)}
    return render_to_response('../templates/forbidden.pt', bindings)
