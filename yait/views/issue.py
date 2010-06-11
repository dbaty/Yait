"""Views related to issues.

$Id$
"""

from datetime import datetime

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.chameleon_zpt import render_template_to_response

from storm.locals import AutoReload

from yait.forms import AddChange
from yait.forms import AddIssue
from yait.models import _getStore
from yait.models import Change
from yait.models import Issue
from yait.models import Project
from yait.utils import renderReST
from yait.views.utils import hasPermission
from yait.views.utils import PERM_PARTICIPATE_IN_PROJECT
from yait.views.utils import PERM_VIEW_PROJECT
from yait.views.utils import PERM_SEE_PRIVATE_TIMING_INFO
from yait.views.utils import TemplateAPI


def issue_add_form(context, request, form=None):
    store = _getStore()
    project = store.find(Project, name=context.project_name).one()
    if not hasPermission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    if form is None:
        form = AddIssue()
    return render_template_to_response('templates/issue_add_form.pt',
                                       api=api,
                                       project=project,
                                       form=form)


def addIssue(context, request):
    form = AddIssue(request.POST)
    if not form.validate():
        return issue_add_form(context, request, form)

    store = _getStore()
    project = store.find(Project, name=context.project_name).one()
    if not hasPermission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()

    last_ref = store.execute(
        'SELECT MAX(ref) FROM issues '
        'WHERE project_id=%d' % project.id).get_one()[0]
    if last_ref is None:
        last_ref = 0
    ref = last_ref + 1
    reporter = u'damien.baty' ## FIXME
    now = datetime.now()

    ## FIXME: I am still not sure that this is a good idea to store
    ## the text of the issue as a comment. I am afraid it may cause
    ## some problems later. I do not see any added value to this apart
    ## from _not_ setting the time spent on the Issue model iself.
    issue = Issue(project_id=project.id,
                  date_created=now,
                  date_edited=now,
                  reporter=reporter,
                  ref=ref)
    form.populate_obj(issue)
    store.add(issue)
    issue.id = AutoReload
    change = Change(issue_id=issue.id,
                    author=reporter,
                    date=now,
                    changes={})
    form.populate_obj(change)
    store.add(change)
    url = '%s/%s/%d' % (
        request.application_url, project.name, issue.ref)
    return HTTPFound(location=url)


def issue_view(context, request, form=None):
    project_name = context.project_name
    store = _getStore()
    project = store.find(Project, name=project_name).one()
    if not hasPermission(request, PERM_VIEW_PROJECT, project):
        return HTTPUnauthorized()

    issue_ref = int(context.issue_ref)
    issue = store.find(
        Issue, project_id=project.id, ref=issue_ref).one()
    if form is None:
        form = AddChange(assignee=issue.assignee,
                         children=issue.getChildren(),
                         deadline=issue.deadline,
                         kind=issue.kind,
                         parent=issue.getParent(),
                         priority=issue.priority,
                         status=issue.status,
                         time_estimated=issue.time_estimated,
                         time_billed=issue.time_billed,
                         title=issue.title)
    api = TemplateAPI(context, request)
    ## FIXME: list(changes) issues an additional SELECT.
    return render_template_to_response('templates/issue_view.pt',
                                       api=api,
                                       project=project,
                                       issue=issue,
                                       changes=issue.getChanges(),
                                       form=form)

def issue_update(context, request):
    project_name = context.project_name
    store = _getStore()
    project = store.find(Project, name=project_name).one()
    if not hasPermission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()

    issue_ref = int(context.issue_ref)
    issue = store.find(
        Issue, project_id=project.id, ref=issue_ref).one()
    userid = u'damien.baty' ## FIXME

    form = AddChange(request.POST)
    if not form.validate():
        return issue_view(context, request, form)

    now = datetime.now()
    changes = {}
    for attr in (
        'status', 'assignee', 'deadline', 'priority', 'kind',
        'time_estimated', 'time_billed'):
        old_v = getattr(issue, attr)
        new_v = getattr(form, attr).data
        if old_v != new_v:
            changes[attr] = (old_v, new_v)
            setattr(issue, attr, new_v)

    ## FIXME: to be implemented
#     current_parent = issue.getParent()
#     new_parent = form.values['parent']
#     if current_parent != new_parent:
#         changes['parent'] = (current_parent, new_parent)
#         issue.setParent(new_parent)
#     current_children = issue.getChidrenIds()
#     new_children = sorted(form.values['children'])
#     if current_children != new_children:
#         changes['children'] = (current_children, new_children)
#         issue.setChildren(new_children)

    change = Change(issue_id=issue.id,
                    author=userid,
                    date=now,
                    text=form.text.data)
    if form.time_spent_real.data and \
            hasPermission(request, PERM_SEE_PRIVATE_TIMING_INFO, project):
        change.time_spent_real = form.time_spent_real.data
        changes['time_spent_real'] = (None, change.time_spent_real)
    if form.time_spent_public.data:
        change.time_spent_public = form.time_spent_public.data
        changes['time_spent_public'] = (None, change.time_spent_public)

    if not changes and not form.text.data:
        ## FIXME: redisplay update form with an appropriate general
        ## error message.
        ## FIXME: and rollback changes made on 'issue' and 'change'!
        raise NotImplementedError

    change.changes = changes
    store.add(change)
    change.id = AutoReload
    url = '%s/%s/%d?issue_updated=1#issue_updated' % (
        request.application_url, project.name, issue.ref)
    return HTTPFound(location=url)


def ajax_renderReST(context, request):
    """Render reStructuredText (called via AJAX)."""
    text = request.params.get('text', '')
    return dict(rendered=renderReST(text))
