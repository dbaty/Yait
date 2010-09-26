"""Views related to the site.

$Id$
"""

from urllib import quote_plus

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.renderers import render_to_response

from yait.models import Admin
from yait.models import DBSession
from yait.models import Project
from yait.models import Role
from yait.views.utils import get_user_metadata
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import TemplateAPI


def site_index(context, request):
    """Index page of Yait."""
    session = DBSession()
    api = TemplateAPI(context, request)
    is_admin = api.has_permission(PERM_ADMIN_SITE)
    if is_admin:
        projects = session.query(Project)
    elif api.logged_in:
        public = session.query(Project).filter_by(public=True)
        has_role = session.query(Project).join(Role).filter(
            Project.id == Role.project_id)
        projects = has_role.union(public)
    else:
        projects = session.query(Project).filter_by(public=True)
    projects = projects.order_by(Project.title).all()

    ## FIXME: we should probably also list open issues assigned to the
    ## logged-in users, here.
    return render_to_response('templates/site_index.pt',
                              dict(api=api,
                                   projects=projects))


def control_panel(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    return render_to_response('templates/site_control_panel.pt',
                              dict(api=api))


def manage_admins_form(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    admins = session.query(Admin).order_by(Admin.user_id).all()
    api = TemplateAPI(context, request)
    user_id = get_user_metadata(request)['uid']
    return render_to_response('templates/site_manage_admins_form.pt',
                              dict(api=api,
                                   current_user_id=user_id,
                                   admins=admins))


def add_admin(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST['admin_id']
    if not admin_id:
        msg = quote_plus(u'Please provide an user id.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    ## FIXME: check that admin_id exists in the user source.
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


def delete_admin(context, request):
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
    

def manage_projects_form(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    api = TemplateAPI(context, request)
    return render_to_response('templates/site_manage_projects_form.pt',
                              dict(api=api,
                                   projects=projects))


def delete_project(context, request):
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


def not_found(context, request):
    api = TemplateAPI(context, request)
    response = render_to_response(
        'templates/notfound.pt',
        value=dict(api=api,
                   resource_url=request.url))
    response.status = 404
    return response
