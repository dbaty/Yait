"""View related to projects."""


from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.forms import AddProjectForm
from yait.models import DBSession
from yait.models import Project
from yait.views.utils import has_permission
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import PERM_VIEW_PROJECT
from yait.views.utils import TemplateAPI


def add_form(request, form=None):
    if not has_permission(request, PERM_ADMIN_SITE):
        raise HTTPForbidden()
    if form is None:
        form = AddProjectForm()
    bindings = {'api': TemplateAPI(request),
                'form': form}
    return render_to_response('../templates/project_add.pt', bindings)


def add(request):
    if not has_permission(request, PERM_ADMIN_SITE):
        raise HTTPForbidden()
    form = AddProjectForm(request.POST)
    if not form.validate():
        return add_form(request, form)
    project = Project()
    form.populate_obj(project)
    session = DBSession()
    session.add(project)
    # FIXME: use 'request.route_url()'
    url = '%s/%s' % (request.application_url, project.name)
    return HTTPSeeOther(location=url)


def home(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()

    ## FIXME:
    ## - list of issues assigned to the current user
    ## - list of top master issues (issues without any parent)
    ## - list of recently edited/commented issues
    ## - link to the tree view;
    ## anything else?

    if not has_permission(request, PERM_VIEW_PROJECT, project):
        raise HTTPForbidden()
    bindings = {'api': TemplateAPI(request),
                'project': project}
    return render_to_response('../templates/project.pt', bindings)


def configure_form(request):
    # FIXME
    from pyramid.response import Response
    return Response('configuration form (to do)')


def search_form(request):
    # FIXME
    from pyramid.response import Response
    return Response('search form (to do)')
