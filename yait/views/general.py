"""Views related to Yait in general.

(I know that the name of this module is not particularly meaningful
but I could not call it 'yait' because imports from ``yait.utils``
then fail in this sub-package.)

$Id$
"""

from repoze.bfg.chameleon_zpt import render_template_to_response

from yait.models import _getStore
from yait.models import Project
from yait.views.utils import TemplateAPI


def yait_index(context, request):
    """Index page of Yait."""
    ## This page is accessible to anonymous users.
    ## FIXME:
    ## - list of accessible projects
    ## - list of issues assigned to the current user (?)
    store = _getStore()
    projects = store.find(Project)
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/yait_index.pt',
                                       api=api,
                                       projects=projects)
