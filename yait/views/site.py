"""General purpose views: home page, not found, etc."""

from pyramid.renderers import render_to_response

from yait.views.utils import TemplateAPI


def home(request):
    """Index page of Yait."""
    api = TemplateAPI(request)
    bindings = {'api': api,
                'projects': api.all_projects}
    return render_to_response('../templates/home.pt', bindings)


def not_found(request):
    bindings = {'api': TemplateAPI(request)}
    response = render_to_response('../templates/notfound.pt', bindings)
    response.status = 404
    return response
