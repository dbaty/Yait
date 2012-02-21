"""Global management interfaces."""

from urllib import quote_plus

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response

from sqlalchemy.orm.exc import NoResultFound

from yait.models import DBSession
from yait.models import Project
from yait.models import User
from yait.views.utils import TemplateAPI


def control_panel(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    bindings = {'api': TemplateAPI(request)}
    return render_to_response('../templates/control_panel.pt', bindings)


def list_admins(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    admins = session.query(User).filter_by(
        is_admin=True).order_by(User.fullname).all()
    bindings = {'api': TemplateAPI(request),
                'current_user_id': request.user.id,
                'admins': admins}
    return render_to_response('../templates/list_admins.pt', bindings)


def add_admin(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    user_id = request.POST['user_id']
    if not user_id:
        # FIXME: use 'request.route_url()'
        msg = quote_plus(u'Please provide an user id.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    session = DBSession()
    try:
        user = session.query(User).filter_by(id=user_id).one()
    except NoResultFound:
        msg = quote_plus(u'User could not be found.')
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    if user.is_admin:
        # FIXME: use 'request.route_url()'
        msg = quote_plus(u'User "%s" is already an administrator.' % user.fullname)
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    user.is_admin = True
    msg = quote_plus(u'User "%s" is now an administrator.' % user.fullname)
    # FIXME: use 'request.route_url()'
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)


def delete_admin(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    admin_id = request.POST['admin_id']
    if not admin_id:
        msg = quote_plus(u'Please provide an user id.')
        # FIXME: use 'request.route_url()'
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    if admin_id == request.user.id:
        msg = quote_plus(u'You cannot remove yourself. Hopefully.')
        # FIXME: use 'request.route_url()'
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    session = DBSession()
    try:
        admin = session.query(User).filter_by(id=admin_id).one()
    except NoResultFound:
        msg = quote_plus(u'User could not be found.' % admin_id)
        url = '%s/control_panel/manage_admins_form?error_message=%s' % (
            request.application_url, msg)
        return HTTPSeeOther(location=url)
    admin.is_admin = False
    # FIXME: be more precise and indicate that the user still exists
    # and provide a link to deactivate the account.
    msg = quote_plus(u'User "%s" is not an administrator anymore.' % admin_id)
    # FIXME: use 'request.route_url()'
    url = '%s/control_panel/manage_admins_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)
    

def list_projects(request):
    if not request.user.is_admin:
        raise HTTPForbidden()
    session = DBSession()
    projects = session.query(Project).order_by(Project.title).all()
    bindings = {'api': TemplateAPI(request),
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
    msg = quote_plus(u'Project "%s" ("%s") has been deleted.' % (
            name, title))
    # FIXME: use 'request.route_url()'    
    url = '%s/control_panel/manage_projects_form?status_message=%s' % (
        request.application_url, msg)
    return HTTPSeeOther(location=url)
