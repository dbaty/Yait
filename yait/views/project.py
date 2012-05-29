from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response

from sqlalchemy import distinct
from sqlalchemy.orm.exc import NoResultFound

from yait.auth import has_permission
from yait.auth import PERM_MANAGE_PROJECT
from yait.auth import PERM_PARTICIPATE_IN_PROJECT
from yait.auth import PERM_VIEW_PROJECT
from yait.auth import ROLE_LABELS
from yait.forms import make_edit_project_form
from yait.forms import make_simplified_search_form
from yait.i18n import _
from yait.models import Change
from yait.models import CHANGE_ACTIONS
from yait.models import DBSession
from yait.models import DEFAULT_STATUSES
from yait.models import Issue
from yait.models import ISSUE_STATUS_CLOSED
from yait.models import Project
from yait.models import Role
from yait.models import Status
from yait.models import User
from yait.views.utils import TemplateAPI


RECENT_ACTIVITY_LENGTH = 10


def home(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        raise HTTPForbidden()
    can_participate = has_permission(
        request, PERM_PARTICIPATE_IN_PROJECT, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    issues = session.query(Issue.id).filter_by(project_id=project.id).\
        filter(Issue.status!=ISSUE_STATUS_CLOSED)
    n_assigned = issues.filter_by(assignee=request.user.id).count()
    n_watching = 0  # FIXME
    n_not_assigned = issues.filter_by(assignee=None).count()
    search_form = make_simplified_search_form(project, session)
    recent_activity = get_recent_activity(session, project, request)
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_participate': can_participate,
                'can_manage_project': can_manage_project,
                'n_assigned': n_assigned,
                'n_watching': n_watching,
                'n_not_assigned': n_not_assigned,
                'search_form': search_form,
                'recent_activity': recent_activity}
    return render_to_response('../templates/project.pt', bindings)


def recent_activity(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        raise HTTPForbidden()
    can_participate = has_permission(
        request, PERM_PARTICIPATE_IN_PROJECT, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    recent_activity = get_recent_activity(session, project, request)
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_participate': can_participate,
                'can_manage_project': can_manage_project,
                'recent_activity': recent_activity}
    return render_to_response(
        '../templates/project_recent_activity.pt', bindings)


def get_recent_activity(db_session, project, request):
    """Return a list of strings that describe the recent activity in
    the given ``project``.
    """
    activity = []
    for issue, change in db_session.query(Issue, Change).\
            filter(Change.project_id==project.id).\
            filter(Issue.id==Change.issue_id).\
            order_by(Change.date.desc()).\
            limit(RECENT_ACTIVITY_LENGTH).all():
        action = _(CHANGE_ACTIONS[change.type])
        issue_url = request.route_url(
            'issue_view', project_name=project.name, issue_ref=issue.ref)
        change_url = '%s#change-%d' % (issue_url, change.id)
        info = {'author': request.cache.fullnames[change.author],
                'action': action,
                'issue_ref': issue.ref,
                'issue_url': issue_url,
                'change_url': change_url,
                'title': issue.title}
        msg = _('${author} <a href="${change_url}">${action}</a> issue '
                '<a href="${issue_url}">#${issue_ref}: ${title}</a>.') % info
        activity.append({'desc': msg, 'text': change.get_rendered_text()})
    return activity


def issues(request):
    """A list of issues that correspond to the filter requested in the
    GET parameters.
    """
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_VIEW_PROJECT, project):
        raise HTTPForbidden()
    can_participate = has_permission(
        request, PERM_PARTICIPATE_IN_PROJECT, project)
    can_manage_project = has_permission(request, PERM_MANAGE_PROJECT, project)
    issues = session.query(Issue).filter_by(project_id=project.id).\
        filter(Issue.status!=ISSUE_STATUS_CLOSED)
    filter = request.GET.get('filter')
    if filter == 'assigned-to-me':
        issues = issues.filter_by(assignee=request.user.id)
        filter_label = _('Assigned to me')
    elif filter == 'watching':
        # FIXME: not implemented yet
        filter_label = None
    elif filter == 'not-assigned':
        filter_label = _('Not assigned')
        issues = issues.filter_by(assignee=None)
    else:
        filter_label = None
        issues = ()
    if issues:
        issues = issues.all()
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_participate': can_participate,
                'can_manage_project': can_manage_project,
                'filter': filter,
                'filter_label': filter_label,
                'issues': issues,
                'count': len(issues)}
    return render_to_response(
        '../templates/project_issues.pt', bindings)


def configure_form(request, form=None):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    if form is None:
        data = {'title': project.title,
                'public': project.public}
        form = make_edit_project_form(**data)
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_manage_project': True,
                'form': form}
    return render_to_response('../templates/project_configure.pt', bindings)


def configure(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    form = make_edit_project_form(request.POST)
    if not form.validate():
        return configure_form(request, form)
    project.update(**form.data)
    msg = _(u'Changes have been saved.')
    request.session.flash(msg, 'success')
    url = request.route_url('project_configure', project_name=project.name)
    return HTTPSeeOther(url)


def configure_roles_form(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    roles = []
    for role_id, label in ROLE_LABELS.items():
        roles.append({'id': role_id, 'label': label})
    user_roles = []
    for role, user in session.query(Role, User).\
            filter(Role.project_id==project.id).\
            filter(Role.user_id==User.id).\
            order_by(User.fullname):
        user_roles.append({'user_id': user.id,
                           'fullname': user.fullname,
                           'role': role.role})
    if request.user.is_admin:
        ids_with_role = [u['user_id'] for u in user_roles]
        users_with_no_role = [{'id': 0, 'fullname': _(u'Select a user...')}]
        # 'ids_with_role' may be empty. SQLAlchemy informs us in this
        # case that
        #     the IN-predicate on "users.id" was invoked with an empty
        #     sequence. This results in a contradiction, which
        #     nonetheless can be expensive to evaluate.
        # Hence the construction of a tuple that contains at least -1 (an
        # impossible user id).
        for user in session.query(User).\
                filter(~User.id.in_((-1, ) + tuple(ids_with_role))).\
                filter_by(is_admin=False).\
                order_by(User.fullname):
            users_with_no_role.append({'id': user.id,
                                       'fullname': user.fullname})
    else:
        # Project managers are not allowed to grant a role to users
        # who do not have a prior role in the project.
        users_with_no_role = ()
    bindings = {'api': TemplateAPI(request, project.title),
                'can_manage_project': True,
                'project': project,
                'roles': roles,
                'user_roles': user_roles,
                'users_with_no_role': users_with_no_role}
    return render_to_response('../templates/project_roles.pt', bindings)


def configure_roles(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    current_roles = {}
    for role in session.query(Role).filter_by(project_id=project.id):
        current_roles[role.user_id] = role.role
    updated_roles = []
    for field, role_id in request.POST.items():
        if not field.startswith('role_'):  # pragma: no cover
            continue
        user_id = int(field[1 + field.rfind('_'):])
        if not request.user.is_admin:
            if user_id == request.user.id:
                # Manager cannot revoke his/her own manager role. This
                # is not allowed by the UI but we handle the case
                # anyway.
                msg = _(u'You cannot revoke your own manager role.')
                request.session.flash(msg, 'error')
                return configure_roles_form(request)
            if user_id not in current_roles:
                # A non-administrator cannot grant a role to a user
                # who has no prior role in this project. This is not
                # allowed by the UI but we handle the case anyway.
                msg = _(u'Granting a role to a new user is not allowed '
                        u'because you are not an administrator.')
                request.session.flash(msg, 'error')
                return configure_roles_form(request)
        role_id = int(role_id)
        if role_id:
            updated_roles.append(Role(project_id=project.id,
                                      user_id=user_id,
                                      role=role_id))
    session.query(Role).filter_by(project_id=project.id).delete()
    session.add_all(updated_roles)
    request.session.flash(_(u'Roles have been updated'), 'success')
    location = request.route_url('project_configure_roles',
                                 project_name=project.name)
    return HTTPSeeOther(location=location)


def configure_statuses_form(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    used = [s[0] for s in session.query(distinct(Issue.status)).\
        filter_by(project_id=project.id).all()]
    # FIXME: We may want to include default statuses in 'used' as well.
    bindings = {'api': TemplateAPI(request, project.title),
                'project': project,
                'can_manage_project': True,
                'used': used}
    return render_to_response('../templates/project_statuses.pt', bindings)


def configure_statuses(request):
    project_name = request.matchdict['project_name']
    session = DBSession()
    try:
        project = session.query(Project).filter_by(name=project_name).one()
    except NoResultFound:
        raise HTTPNotFound()
    if not has_permission(request, PERM_MANAGE_PROJECT, project):
        raise HTTPForbidden()
    posted_statuses = map(int, request.POST.getall('statuses'))
    # The UI should not allow to remove default statuses, but let's
    # enforce it here.
    for default_status in DEFAULT_STATUSES:
        if default_status['id'] not in posted_statuses:
            msg = _('You cannot remove this status.')
            request.session.flash(msg, 'error')
            return configure_statuses_form(request)
    # The UI should not allow to remove statuses that are being used,
    # but let's enforce it here.
    # FIXME: to do
    current_statuses = {}
    for status in project.statuses:
        current_statuses[status.id] = status
    statuses = zip(posted_statuses, request.POST.getall('labels'))
    # Change existing statuses and add new ones
    new_id = session.execute(
        'SELECT MAX(id) FROM statuses '
        'WHERE project_id=%d' % project.id).fetchone()[0]
    for position, (status_id, label) in enumerate(statuses, 1):
        if not status_id:
            new_id += 1
            status = Status(id=new_id, project_id=project.id,
                            label=label, position=position)
            session.add(status)
        else:
            status = current_statuses[status_id]
            if label != status.label:
                status.label = label
            if position != status.position:
                status.position = position
    # Remove statuses
    for status in project.statuses:
        if status.id not in posted_statuses:
            session.delete(status)
    msg = _('Your changes have been saved.')
    request.session.flash(msg, 'success')
    url = request.route_url('project_configure_statuses',
                            project_name=project.name)
    return HTTPSeeOther(location=url)


def search_form(request):
    # FIXME
    from pyramid.response import Response
    return Response('search form (to do)')
