"""Views related to issues.

$Id$
"""

from datetime import datetime

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.chameleon_zpt import render_template_to_response

from storm.locals import AutoReload

from yait.forms import ChangeAddForm
from yait.forms import IssueAddForm
from yait.models import _getStore
from yait.models import Change
from yait.models import Issue
from yait.models import Project
from yait.utils import renderReST
from yait.utils import timeToStr
from yait.views.utils import hasPermission
from yait.views.utils import PERM_ADMIN_PROJECT
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
        form = IssueAddForm()
    return render_template_to_response('templates/issue_add_form.pt',
                                       api=api,
                                       project=project,
                                       form=form)


def addIssue(context, request):
    ## FIXME: check authorization
    form = IssueAddForm(request.params)
    if not form.validate():
        return issue_add_form(context, request, form)

    form.convertValues()
    store = _getStore()
    project = store.find(Project, name=context.project_name).one()

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
                  ref=ref,
                  reporter=reporter,
                  title=form.values['title'],
                  assignee=form.values['assignee'],
                  kind=form.values['kind'],
                  priority=form.values['priority'],
                  status=form.values['status'],
                  date_created=now,
                  date_edited=now,
                  deadline=form.values['deadline'] or None, ## FIXME: should be converted in 'IssueAddForm.convertValue()'
                  time_estimated=form.values['time_estimated'],
                  time_billed=form.values['time_billed'])
    store.add(issue)
    issue.id = AutoReload
    change = Change(issue_id=issue.id,
                    author=reporter,
                    date=now,
                    time_spent=form.values['time_spent'],
                    text=form.values['text'],
                    changes={})
    store.add(change)
    url = '%s/%s/%d' % (
        request.application_url, project.name, issue.ref)
    return HTTPFound(location=url)


def issue_view(context, request, form=None):
    project_name = context.project_name
    issue_ref = int(context.issue_ref)
    store = _getStore()
    project = store.find(Project, name=project_name).one()
    issue = store.find(
        Issue, project_id=project.id, ref=issue_ref).one()
    changes = store.find(Change, issue_id=issue.id).order_by(Change.id)
    if form is None:
        defaults = dict(
            assignee=issue.assignee,
            children=issue.getChildren(),
            deadline=issue.deadline, ## FIXME: must be converted back to str
            kind=issue.kind,
            parent=issue.getParent(),
            priority=issue.priority,
            status=issue.status,
            time_estimated=timeToStr(issue.time_estimated),
            title=issue.title)
        form = ChangeAddForm(defaults)
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/issue_view.pt',
                                       api=api,
                                       project=project,
                                       issue=issue,
                                       changes=list(changes),
                                       form=form)

def issue_update(context, request):
    ## FIXME: check authorization
    project_name = context.project_name
    issue_ref = int(context.issue_ref)
    store = _getStore()
    project = store.find(Project, name=project_name).one()
    issue = store.find(
        Issue, project_id=project.id, ref=issue_ref).one()
    userid = u'damien.baty' ## FIXME

    form = ChangeAddForm(request.params)
    if not form.validate():
        return issue_view(context, request, form)

    form.convertValues()
    now = datetime.now()
    changes = {}
    for attr in (
        'status', 'assignee', 'time_estimated', 'time_billed',
        'deadline', 'priority', 'kind'):
        old_v = getattr(issue, attr)
        new_v = form.values[attr]
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
                    text=form.values['text'], 
                    time_spent=form.values['time_spent'],
                    changes=changes)
    store.add(change)
    change.id = AutoReload
    url = '%s/%s/%d#%d' % (
        request.application_url, project.name, issue.ref, change.id)
    return HTTPFound(location=url)


def ajax_renderReST(context, request):
    """Render reStructuredText (called via AJAX)."""
    text = request.params.get('text', '')
    return dict(rendered=renderReST(text))
