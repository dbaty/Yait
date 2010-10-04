"""Views related to issues.

$Id$
"""

from datetime import datetime

from webob.exc import HTTPFound
from webob.exc import HTTPUnauthorized

from repoze.bfg.chameleon_zpt import render_template_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.forms import AddChangeForm
from yait.forms import AddIssueForm
from yait.models import Change
from yait.models import DBSession
from yait.models import Issue
from yait.models import Project
from yait.utils import render_ReST
from yait.views.site import not_found
from yait.views.utils import get_user_metadata
from yait.views.utils import has_permission
from yait.views.utils import PERM_PARTICIPATE_IN_PROJECT
from yait.views.utils import PERM_VIEW_PROJECT
from yait.views.utils import PERM_SEE_PRIVATE_TIMING_INFO
from yait.views.utils import TemplateAPI


def add_issue_form(context, request, form=None):
    session = DBSession()
    project_name = request.matchdict['project_name']
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        return not_found(context, request)        
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()
    api = TemplateAPI(context, request)
    if form is None:
        form = AddIssueForm()
    return render_template_to_response('templates/issue_add_form.pt',
                                       api=api,
                                       project=project,
                                       form=form)


def add_issue(context, request):
    session = DBSession()
    project_name = request.matchdict['project_name']
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        return not_found(context, request)
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()
    form = AddIssueForm(request.POST)
    if not form.validate():
        return add_issue_form(context, request, form)

    last_ref = session.execute(
        'SELECT MAX(ref) FROM issues '
        'WHERE project_id=%d' % project.id).fetchone()[0]
    if last_ref is None:
        last_ref = 0
    ref = last_ref + 1
    reporter = get_user_metadata(request)['uid']
    now = datetime.now()
    issue = Issue(project_id=project.id,
                  date_created=now,
                  date_edited=now,
                  reporter=reporter,
                  ref=ref)
    form.populate_obj(issue)
    session.add(issue)
    session.flush()
    change = Change(issue_id=issue.id,
                    author=reporter,
                    date=now,
                    changes={})
    form.populate_obj(change)
    session.add(change)
    url = '%s/%s/%d' % (
        request.application_url, project.name, issue.ref)
    return HTTPFound(location=url)


def issue_view(context, request, form=None):
    project_name = request.matchdict['project_name']
    issue_ref = int(request.matchdict['issue_ref'])
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        return not_found(context, request)
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        return HTTPUnauthorized()
    try:
        issue = session.query(Issue).filter_by(
            project_id=project.id, ref=issue_ref).one()
    except NoResultFound:
        return not_found(context, request)
    if form is None:
        form = AddChangeForm(assignee=issue.assignee,
                             children=issue.get_children(),
                             deadline=issue.deadline,
                             kind=issue.kind,
                             parent=issue.get_parent(),
                             priority=issue.priority,
                             status=issue.status,
                             time_estimated=issue.time_estimated,
                             time_billed=issue.time_billed,
                             title=issue.title)
    api = TemplateAPI(context, request)
    return render_template_to_response('templates/issue_view.pt',
                                       api=api,
                                       project=project,
                                       issue=issue,
                                       form=form,
                                       now=datetime.now())

def issue_update(context, request):
    project_name = request.matchdict['project_name']
    issue_ref = int(request.matchdict['issue_ref'])
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        return not_found(context, request)
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        return HTTPUnauthorized()
    try:
        issue = session.query(Issue).filter_by(
            project_id=project.id, ref=issue_ref).one()
    except NoResultFound:
        return not_found(context, request)

    form = AddChangeForm(request.POST)
    if not form.validate():
        return issue_view(context, request, form)

    now = datetime.now()
    userid = u'damien.baty' ## FIXME
    changes = {}
    for attr in (
        'status', 'assignee', 'deadline', 'priority', 'kind',
        'time_estimated', 'time_billed'):
        old_v = getattr(issue, attr)
        new_v = getattr(form, attr).data
        if attr.startswith('time_') and not new_v:
            ## FIXME: probably nto the right way to do it
            new_v = 0
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
            has_permission(request, PERM_SEE_PRIVATE_TIMING_INFO, project):
        change.time_spent_real = form.time_spent_real.data
        changes['time_spent_real'] = (None, change.time_spent_real)
    if form.time_spent_public.data:
        change.time_spent_public = form.time_spent_public.data
        changes['time_spent_public'] = (None, change.time_spent_public)

    if not changes and not form.text.data:
        ## FIXME: move this test above before we add 'Change' so we do
        ## not have to rollback anything.
        ## FIXME: redisplay update form with an appropriate general
        ## error message.
        ## FIXME: and rollback changes made on 'issue' and 'change'!
        raise NotImplementedError

    change.changes = changes
    session.add(change)
    session.flush()
    url = '%s/%s/%d?issue_updated=1#issue_updated' % (
        request.application_url, project.name, issue.ref)
    return HTTPFound(location=url)


def ajax_render_ReST(context, request):
    """Render reStructuredText (called via AJAX)."""
    text = request.params.get('text', '')
    return {'rendered': render_ReST(text)}
