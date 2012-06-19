from yait.views.utils import TemplateAPI


def prefs(request):
    api = TemplateAPI(request)
    return {'api': api}
