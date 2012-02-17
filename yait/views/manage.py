"""Global management interfaces."""

from urllib import quote_plus

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.renderers import render_to_response

from yait.models import Admin
from yait.models import DBSession
from yait.models import Project
from yait.views.utils import get_user_metadata
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import TemplateAPI


def control_panel(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    api = TemplateAPI(request)
    return render_to_response('../templates/site_control_panel.pt',
                              {'api': api})


def list_admins(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    admins = session.query(Admin).order_by(Admin.user_id).all()
    api = TemplateAPI(request)
    user_id = get_user_metadata(request)['uid']
    return render_to_response('../templates/site_manage_admins_form.pt',
                              {'api': api,
                               'current_user_id': user_id,
                               'admins': admins})


def add_admin(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST['admin_id']
    if not admin_id:
        msg = quote_plus(u'Please provide an user id.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    # FIXME: check that admin_id exists in the user source.
    session = DBSession()
    if session.query(Admin).filter_by(user_id=admin_id).count():
        msg = quote_plus(u'User "%s" is already an administrator.' % admin_id)
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    admin = Admin(user_id=admin_id)
    session.add(admin)
    msg = quote_plus(u'User "%s" is now an administrator.' % admin_id)
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)


def delete_admin(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST['admin_id']
    if not admin_id:
        msg = quote_plus(u'Please provide an user id.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    if admin_id == get_user_metadata(request)['uid']:
        msg = quote_plus(u'You cannot remove yourself. Hopefully.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    session = DBSession()
    admin = session.query(Admin).filter_by(user_id=admin_id).one()
    session.delete(admin)
    msg = quote_plus(u'User "%s" is not an administrator anymore.' % admin_id)
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)
    

def list_projects(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    api = TemplateAPI(request)
    return render_to_response('../templates/site_manage_projects_form.pt',
                              {'api': api,
                               'projects': projects})


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
    url = '%s/control_panel/manage_projects_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)
