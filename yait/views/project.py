"""View related to projects.

$Id$
"""

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.renderers import render_to_response

from yait.forms import AddProject
from yait.models import DBSession
from yait.models import Issue
from yait.models import Project
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import PERM_VIEW_PROJECT
from yait.views.utils import TemplateAPI

def add_project_form(context, request, form=None):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    if form is None:
        form = AddProject()
    return render_to_response('templates/project_add_form.pt',
                              dict(api=api, form=form))


def add_project(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    form = AddProject(request.POST)
    if not form.validate():
        return add_project_form(context, request, form)

    project = Project()
    form.populate_obj(project)
    store = _getStore()
    store.add(project)
    url = '%s/%s' % (request.application_url, project.name)
    return HTTPFound(location=url)


def project_view(context, request):
    ## FIXME:
    ## - list of issues assigned to the current user
    ## - list of top master issues (issues without any parent)
    ## - list of recently edited/commented issues
    ## - link to the tree view;
    ## anything else?
    project_name = context.project_name
    store = _getStore()
    project = store.find(Project, name=project_name).one()
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        return HTTPUnauthorized()
    issues = store.find(Issue, project_id=project.id)
    api = TemplateAPI(context, request)
    return render_to_response('templates/project_view.pt',
                              dict(api=api,
                                   project=project,
                                   issues=issues))


def project_tree_view(context, request):
    ## a tree view of issues (more precisely, a graph, since there may
    ## be more than one top master issues).
    raise NotImplementedError ## FIXME
