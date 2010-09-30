"""View related to projects.

$Id$
"""

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.forms import AddProjectForm
from yait.models import DBSession
from yait.models import Project
from yait.views.site import not_found
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import PERM_VIEW_PROJECT
from yait.views.utils import TemplateAPI


def add_project_form(context, request, form=None):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    if form is None:
        form = AddProjectForm()
    return render_to_response('templates/project_add_form.pt',
                              {'api': api, 'form': form})


def add_project(context, request):
    if not has_permission(request, PERM_ADMIN_SITE):
        return HTTPUnauthorized()
    form = AddProjectForm(request.POST)
    if not form.validate():
        return add_project_form(context, request, form)

    project = Project()
    form.populate_obj(project)
    session = DBSession()
    session.add(project)
    url = '%s/%s' % (request.application_url, project.name)
    return HTTPFound(location=url)


def project_view(context, request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        return not_found(context, request)

    ## FIXME:
    ## - list of issues assigned to the current user
    ## - list of top master issues (issues without any parent)
    ## - list of recently edited/commented issues
    ## - link to the tree view;
    ## anything else?

    if not has_permission(request, PERM_VIEW_PROJECT, project):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    return render_to_response('templates/project_view.pt',
                              {'api': api,
                               'project': project})
