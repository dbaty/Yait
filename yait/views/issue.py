"""Views related to issues."""


from datetime import datetime

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.auth import has_permission
from yait.auth import PERM_MANAGE_PROJECT
from yait.auth import PERM_PARTICIPATE_IN_PROJECT
from yait.auth import PERM_SEE_PRIVATE_TIMING_INFO
from yait.auth import PERM_VIEW_PROJECT
from yait.forms import make_add_change_form
from yait.forms import make_add_issue_form
from yait.i18n import _
from yait.models import Change
from yait.models import CHANGE_TYPE_CLOSING
from yait.models import CHANGE_TYPE_OPENING
from yait.models import CHANGE_TYPE_REOPENING
from yait.models import CHANGE_TYPE_UPDATE
from yait.models import DBSession
from yait.models import Issue
from yait.models import ISSUE_STATUS_CLOSED
from yait.models import ISSUE_STATUS_OPEN
from yait.models import Project
from yait.text import render
from yait.views.utils import TemplateAPI


def add_form(request, form=None):
    session = DBSession()
    project_name = request.matchdict['project_name']
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        raise HTTPForbidden()
    if form is None:
        form = make_add_issue_form(project, session)
    can_see_priv = has_permission(
        request, PERM_SEE_PRIVATE_TIMING_INFO, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    bindings = {'api': TemplateAPI(request, _(u'Add issue')),
                'project': project,
                'form': form,
                'can_see_private_time_info': can_see_priv,
                'can_manage_project': can_manage_project}
    return render_to_response('../templates/issue_add.pt', bindings)


def add(request):
    session = DBSession()
    project_name = request.matchdict['project_name']
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        raise HTTPForbidden()
    form = make_add_issue_form(project, session, request.POST)
    if not form.validate():
        return add_form(request, form)

    last_ref = session.execute(
        'SELECT MAX(ref) FROM issues '
        'WHERE project_id=%d' % project.id).fetchone()[0]
    if last_ref is None:
        last_ref = 0
    ref = last_ref + 1
    reporter = request.user.id
    now = datetime.utcnow()
    issue = Issue(project_id=project.id,
                  date_created=now,
                  date_edited=now,
                  reporter=reporter,
                  ref=ref)
    form.populate_obj(issue)
    session.add(issue)
    session.flush()
    change = Change(project_id=project.id,
                    issue_id=issue.id,
                    type=CHANGE_TYPE_OPENING,
                    author=reporter,
                    date=now,
                    changes={})
    form.populate_obj(change)
    session.add(change)
    route_args = {'project_name': project_name, 'issue_ref': issue.ref}
    url = request.route_url('issue_view', **route_args)
    return HTTPSeeOther(location=url)


def view(request, form=None):
    project_name = request.matchdict['project_name']
    try:
        issue_ref = int(request.matchdict['issue_ref'])
    except ValueError:
        # 'issue_ref' is not an integer. The route connected to this
        # view matched because no other route matched. This could be a
        # typo, for example: '/p/project-foo/confgure'.
        raise HTTPNotFound()
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        raise HTTPForbidden()
    try:
        issue = session.query(Issue).filter_by(
            project_id=project.id, ref=issue_ref).one()
    except NoResultFound:
        raise HTTPNotFound()
    if form is None:
        data = {'assignee': issue.assignee,
                'deadline': issue.deadline,
                'kind': issue.kind,
                'priority': issue.priority,
                'status': issue.status,
                'time_estimated': issue.time_estimated,
                'time_billed': issue.time_billed,
                'title': issue.title}
        form = make_add_change_form(project, session, **data)
    can_see_priv = has_permission(
        request, PERM_SEE_PRIVATE_TIMING_INFO, project)
    can_participate = has_permission(
        request, PERM_PARTICIPATE_IN_PROJECT, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    time_info = issue.get_time_info(include_private_info=can_see_priv)
    bindings = {'api': TemplateAPI(request, issue.title),
                'project': project,
                'issue': issue,
                'time_info': time_info,
                'form': form,
                'can_participate': can_participate,
                'can_manage_project': can_manage_project,
                'can_see_private_time_info': can_see_priv}
    return render_to_response('../templates/issue.pt', bindings)


def update(request):
    project_name = request.matchdict['project_name']
    issue_ref = int(request.matchdict['issue_ref'])
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_PARTICIPATE_IN_PROJECT, project):
        raise HTTPForbidden()
    try:
        issue = session.query(Issue).filter_by(
            project_id=project.id, ref=issue_ref).one()
    except NoResultFound:
        raise HTTPNotFound()

    # FIXME: move logic outside so that it can be more easily tested.
    form = make_add_change_form(project, session, request.POST)
    if not form.validate():
        return view(request, form)
    now = datetime.utcnow()
    userid = request.user.id
    changes = {}
    for attr in (
        'title', 'status', 'assignee', 'deadline', 'priority', 'kind',
        'time_estimated', 'time_billed'):
        old_v = getattr(issue, attr)
        new_v = getattr(form, attr).data
        if old_v != new_v:
            changes[attr] = (old_v, new_v)
            setattr(issue, attr, new_v)
    if form.time_spent_real.data and \
            has_permission(request, PERM_SEE_PRIVATE_TIMING_INFO, project):
        changes['time_spent_real'] = (None, form.time_spent_real.data)
    if form.time_spent_public.data:
        changes['time_spent_public'] = (None, form.time_spent_public.data)

    if not changes and not form.text.data:
        error = _(u'You did not provide any comment or update.')
        form.errors['form'] = [error]
        return view(request, form)

    if form.status.data == ISSUE_STATUS_OPEN and \
            issue.status != ISSUE_STATUS_OPEN:
        change_type = CHANGE_TYPE_REOPENING
    elif form.status.data == ISSUE_STATUS_CLOSED:
        change_type = CHANGE_TYPE_CLOSING
    else:
        change_type = CHANGE_TYPE_UPDATE
    change = Change(project_id=project.id,
                    issue_id=issue.id,
                    type=change_type,
                    author=userid,
                    date=now,
                    text=form.text.data,
                    text_renderer=form.text_renderer.data,
                    changes=changes)
    if 'time_spent_real' in changes:
        change.time_spent_real = form.time_spent_real.data
    if 'time_spent_public' in changes:
        change.time_spent_public = form.time_spent_public.data
    session.add(change)
    route_args = {'project_name': project_name,
                  'issue_ref': issue.ref,
                  '_query': {'issue_updated': 1},
                  '_anchor': 'issue_updated'}
    url = request.route_url('issue_view', **route_args)
    return HTTPSeeOther(location=url)


def ajax_render_text(request):
    """Render text (called via AJAX)."""
    text = request.GET['text']
    renderer_name = request.GET['text_renderer']
    return {'rendered': render(text, renderer_name)}
