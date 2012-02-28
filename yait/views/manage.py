"""Global management interfaces."""

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.i18n import _
from yait.models import DBSession
from yait.models import Project
from yait.models import User
from yait.views.utils import TemplateAPI


def control_panel(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    bindings = {'api': TemplateAPI(request, _(u'Control panel'))}
    return render_to_response('../templates/control_panel.pt', bindings)


def list_admins(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    admins = session.query(User).filter_by(
        is_admin=True).order_by(User.fullname).all()
    bindings = {'api': TemplateAPI(request, _(u'Administrators')),
                'current_user_id': request.user.id,
                'admins': admins}
    return render_to_response('../templates/list_admins.pt', bindings)


def add_admin(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    user_id = request.POST['user_id']
    if not user_id:
        request.session.flash(_(u'Please select a user.'), 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    session = DBSession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        # We should not get there unless the user has been removed or
        # disabled after the form has been loaded.
        request.session.flash(_(u'User could not be found.'), 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    if user.is_admin:
        # We should not get there unless the user has been granted the
        # administrator role after the form has been loaded.
        msg = _(u'%s is already an administrator.' % user.fullname)
        request.session.flash(msg, 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    user.is_admin = True
    msg = _(u'%s is now an administrator.' % user.fullname)
    request.session.flash(msg, 'success')
    url = request.route_url('admins')
    return HTTPSeeOther(location=url)


def delete_admin(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    admin_id = request.POST['admin_id']
    if not admin_id:
        request.session.flash(_(u'Please provide an user id.'), 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    if admin_id == request.user.id:
        msg = _(u'You cannot revoke your own administrator rights.')
        request.session.flash(msg, 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    session = DBSession()
    try:
        admin = session.query(User).filter_by(id=admin_id).one()
    except NoResultFound:
        # We should not get there unless the user has been removed or
        # disabled after the form has been loaded.
        request.session.flash(_(u'User could not be found.'), 'error')
        url = request.route_url('admins')
        return HTTPSeeOther(location=url)
    admin.is_admin = False
    msg = _(u'%s is no longer an administrator.' % admin.fullname)
    request.session.flash(msg, 'success')
    url = request.route_url('admins')
    return HTTPSeeOther(location=url)


def list_projects(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    bindings = {'api': TemplateAPI(request, _(u'Projects')),
                'projects': projects}
    return render_to_response('../templates/list_projects.pt', bindings)


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
