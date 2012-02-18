"""Views related to the site.

$Id$
"""

from pyramid.renderers import render_to_response

from yait.models import DBSession
from yait.models import Project
from yait.models import Role
from yait.views.utils import PERM_ADMIN_SITE
from yait.views.utils import TemplateAPI


def home(request):
    """Index page of Yait."""
    session = DBSession()
    api = TemplateAPI(request)
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
    ## logged-in user, here.
    return render_to_response('../templates/home.pt',
                              {'api': api,
                               'projects': projects})


def not_found(request):
    api = TemplateAPI(request)
    response = render_to_response(
        '../templates/notfound.pt',
        value={'api': api,
               'resource_url': request.url})
    response.status = 404
    return response
