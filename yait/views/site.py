"""General purpose views: home page, not found, etc."""

from pyramid.renderers import render_to_response

from yait.models import DBSession
from yait.models import Project
from yait.models import Role
from yait.views.utils import TemplateAPI


def home(request):
    """Index page of Yait."""
    session = DBSession()
    if request.user.is_admin:
        projects = session.query(Project)
    elif request.user.id:
        public = session.query(Project).filter_by(public=True)
        has_role = session.query(Project).join(Role).filter(
            Project.id == Role.project_id)
        projects = has_role.union(public)
    else:
        projects = session.query(Project).filter_by(public=True)
    projects = projects.order_by(Project.title).all()
    # FIXME: we should probably also list open issues assigned to the
    # logged-in user, here.
    bindings = {'api': TemplateAPI(request),
                'projects': projects}
    return render_to_response('../templates/home.pt', bindings)


def not_found(request):
    bindings = {'api': TemplateAPI(request)}
    response = render_to_response('../templates/notfound.pt', bindings)
    response.status = 404
    return response
