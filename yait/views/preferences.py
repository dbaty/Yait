from pyramid.renderers import render_to_response

from yait.views.utils import TemplateAPI


def prefs(request):
    """Preferences page."""
    api = TemplateAPI(request)
    bindings = {'api': api}
    return render_to_response('../templates/preferences.pt', bindings)
