"""Views related to the site.

$Id$
"""

from urllib import quote_plus

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.chameleon_zpt import render_template_to_response

from yait.models import _getStore
from yait.models import Manager
from yait.models import Project
from yait.views.utils import get_user_metadata
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import TemplateAPI


def site_index(context, request):
    """Index page of Yait."""
    ## This page is accessible to anonymous users.
    ## FIXME:
    ## - list of accessible projects
    ## - list of issues assigned to the current user (?)
    store = _getStore()
    projects = store.find(Project)
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/site_index.pt',
                                       api=api,
                                       projects=projects)


def control_panel(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/site_control_panel.pt',
                                       api=api)


## FIXME: rename as 'manage_admins_form'
def manage_users_form(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    store = _getStore()
    admins = store.find(Manager)
    api = TemplateAPI(context, request)
    user_id = get_user_metadata(request).get('uid', None)
    return render_template_to_response('templates/site_manage_users_form.pt',
                                       api=api,
                                       current_user_id=user_id,
                                       admins=admins)


## FIXME: rename as 'add_admin()'
def addAdmin(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST.get('admin_id')
    ## FIXME: check that admin_id exists in the user source.
    store = _getStore()
    if store.find(Manager, user_id=admin_id).count():
        msg = quote_plus(u'User "%s" is already an administrator.' % admin_id)
        url = '%s/control_panel/manage_users_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPFound(location=url)
    admin = Manager(user_id=admin_id)
    store.add(admin)
    msg = quote_plus(u'User "%s" is now an administrator.' % admin_id)
    url = '%s/control_panel/manage_users_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)
    

## FIXME: rename as 'delete_admin()'
def deleteAdmin(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    admin_id = request.POST.get('admin_id')
    store = _getStore()
    admin = store.find(Manager, user_id=admin_id).one()
    store.remove(admin)
    msg = quote_plus(u'User "%s" is not an administrator anymore.' % admin_id)
    url = '%s/control_panel/manage_users_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)
    

def manage_projects_form(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    store = _getStore()
    projects = store.find(Project).order_by(Project.name)
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/site_manage_projects_form.pt',
                                       api=api,
                                       projects=projects)


## FIXME: rename as 'delete_projects()'
def deleteProject(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    project_id = int(request.POST.get('project_id'))
    store = _getStore()
    project = store.find(Project, id=project_id).one()
    name, title = project.name, project.title
    store.remove(project)
    msg = quote_plus(u'Project "%s" ("%s") has been deleted.' % (
            name, title))
    url = '%s/control_panel/manage_projects_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPFound(location=url)
