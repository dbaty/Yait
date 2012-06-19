"""General purpose views: home page, not found, etc."""

from yait.views.utils import TemplateAPI


def home(request):
    """Index page of Yait."""
    api = TemplateAPI(request)
    return {'api': api,
            'projects': api.all_projects}


def not_found(request):
    request.response.status = 404
    return {'api': TemplateAPI(request)}
