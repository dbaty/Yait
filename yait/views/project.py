from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.auth import has_permission
from yait.auth import PERM_MANAGE_PROJECT
from yait.auth import PERM_PARTICIPATE_IN_PROJECT
from yait.auth import PERM_VIEW_PROJECT
from yait.models import DBSession
from yait.models import Project
from yait.views.utils import TemplateAPI


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
    can_participate = has_permission(
        request, PERM_PARTICIPATE_IN_PROJECT, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_participate': can_participate,
                'can_manage_project': can_manage_project}
    return render_to_response('../templates/project.pt', bindings)


def configure_form(request):
    # FIXME
    from pyramid.response import Response
    return Response('configuration form (to do)')


def search_form(request):
    # FIXME
    from pyramid.response import Response
    return Response('search form (to do)')
