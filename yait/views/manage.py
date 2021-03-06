from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther

from sqlalchemy.orm.exc import NoResultFound

from yait.auth import ROLE_LABELS
from yait.forms import AddProjectForm
from yait.forms import AddUserForm
from yait.forms import EditUserForm
from yait.i18n import _
from yait.models import DBSession
from yait.models import DEFAULT_STATUSES
from yait.models import Project
from yait.models import Role
from yait.models import Status
from yait.models import User
from yait.views.utils import TemplateAPI


def control_panel(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    return {'api': TemplateAPI(request, _(u'Control panel'))}


def list_users(request):
    """List users (in the control panel)."""
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    # FIXME: paginate
    users = session.query(User).order_by(User.fullname).all()
    return {'api': TemplateAPI(request, _(u'Users')),
            'users': users}


def add_user_form(request, form=None):
    if not request.user.is_admin:
        raise HTTPForbidden()
    if form is None:
        form = AddUserForm()
    return {'api': TemplateAPI(request, _(u'Add a new user')),
            'form': form}


def add_user(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    form = AddUserForm(request.POST)
    if not form.validate():
        return add_user_form(request, form)
    data = form.data
    data.pop('password_confirm')
    user = User(**data)
    session = DBSession()
    session.add(user)
    request.session.flash(_(u'User has been added.'), 'success')
    location = request.route_url('users')
    return HTTPSeeOther(location)


def edit_user_form(request, form=None):
    if not request.user.is_admin:
        raise HTTPForbidden()
    user_id = int(request.matchdict['user_id'])
    session = DBSession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        raise HTTPNotFound()
    if form is None:
        form = EditUserForm(obj=user)
    return {'api': TemplateAPI(request, user.fullname),
            'user': user,
            'form': form}


def edit_user(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    user_id = int(request.matchdict['user_id'])
    session = DBSession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        raise HTTPNotFound()
    form = EditUserForm(request.POST)
    if not form.validate():
        return edit_user_form(request, form)
    data = form.data
    if user_id == request.user.id and not form.data['is_admin']:
        msg = _(u"You cannot revoke your own administrator's rights.")
        request.session.flash(msg, 'error')
        return edit_user_form(request, form)
    user.update(**data)
    request.session.flash(_(u'User has been edited.'), 'success')
    location = request.route_url('users')
    return HTTPSeeOther(location)


def list_user_roles(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    user_id = int(request.matchdict['user_id'])
    session = DBSession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        raise HTTPNotFound()
    roles = []
    for role, project in session.query(Role, Project).\
            filter(Role.user_id==user.id).\
            filter(Role.project_id==Project.id).\
            order_by(Project.title):
        roles.append((project, _(ROLE_LABELS[role.role])))
    return {'api': TemplateAPI(request, user.fullname),
            'user': user,
            'roles': roles}


def list_projects(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    return {'api': TemplateAPI(request, _(u'Projects')),
            'projects': projects}


def add_project_form(request, form=None):
    if not request.user.is_admin:
        raise HTTPForbidden()
    if form is None:
        form = AddProjectForm()
    return {'api': TemplateAPI(request, _(u'Add project')),
            'form': form}


def _add_project(db_session, project):
    """Helper method that takes care of adding the project and default
    statuses.

    This is also used in tests.
    """
    db_session.add(project)
    db_session.flush()  # set project.id
    for position, status in enumerate(DEFAULT_STATUSES, 1):
        status = Status(id=status['id'], project_id=project.id,
                        label=status['label'], position=position)
        db_session.add(status)


def add_project(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    form = AddProjectForm(request.POST)
    if not form.validate():
        return add_project_form(request, form)
    project = Project()
    form.populate_obj(project)
    session = DBSession()
    _add_project(session, project)
    # FIXME: we should rather redirect to the configuration page of
    # the project (with a success message).
    url = request.route_url('project_home', project_name=project.name)
    return HTTPSeeOther(location=url)


def delete_project(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    project_id = int(request.POST.get('project_id'))
    session = DBSession()
    project = session.query(Project).filter_by(id=project_id).one()
    name, title = project.name, project.title
    session.delete(project)
    msg = _(u'Project "${name}" ("${title}") has been deleted.') % {
        'name': name, 'title': title}
    request.session.flash(msg, 'success')
    url = request.route_url('projects')
    return HTTPSeeOther(location=url)
