"""Global management interfaces."""

from urllib import quote_plus

from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.renderers import render_to_response

from yait.models import DBSession
from yait.models import Project
from yait.models import User
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import TemplateAPI


def control_panel(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    bindings = {'api': TemplateAPI(request)}
    return render_to_response('../templates/control_panel.pt', bindings)


def list_admins(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    admins = session.query(User).filter_by(
        is_admin=True).order_by(User.fullname).all()
    bindings = {'api': TemplateAPI(request),
                'current_user_id': request.user.id,
                'admins': admins}
    return render_to_response('../templates/list_admins.pt', bindings)


def add_admin(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST['admin_id']
    if not admin_id:
        # FIXME: use 'request.route_url()'
        msg = quote_plus(u'Please provide an user id.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    # FIXME: check that admin_id exists in the user source.
    session = DBSession()
    if session.query(Admin).filter_by(user_id=admin_id).count():
        # FIXME: use 'request.route_url()'
        msg = quote_plus(u'User "%s" is already an administrator.' % admin_id)
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    admin = Admin(user_id=admin_id)
    session.add(admin)
    msg = quote_plus(u'User "%s" is now an administrator.' % admin_id)
    # FIXME: use 'request.route_url()'
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)


def delete_admin(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST['admin_id']
    if not admin_id:
        msg = quote_plus(u'Please provide an user id.')
        # FIXME: use 'request.route_url()'
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    if admin_id == request.user.id:
        msg = quote_plus(u'You cannot remove yourself. Hopefully.')
        # FIXME: use 'request.route_url()'
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    session = DBSession()
    admin = session.query(Admin).filter_by(user_id=admin_id).one()
    session.delete(admin)
    msg = quote_plus(u'User "%s" is not an administrator anymore.' % admin_id)
    # FIXME: use 'request.route_url()'
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)
    

def list_projects(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    bindings = {'api': TemplateAPI(request),
                'projects': projects}
    return render_to_response('../templates/list_projects.pt', bindings)


def delete_project(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    project_id = int(request.POST.get('project_id'))
    session = DBSession()
    project = session.query(Project).filter_by(id=project_id).one()
    name, title = project.name, project.title
    session.delete(project)
    msg = quote_plus(u'Project "%s" ("%s") has been deleted.' % (
            name, title))
    # FIXME: use 'request.route_url()'    
    url = '%s/control_panel/manage_projects_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)
