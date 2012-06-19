import dogpile.cache

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from yait.auth import AuthorizationPolicy
from yait.cache import register_cache_region
from yait.models import initialize_sql


def _set_auth_policies(config, settings,
                       _auth_policy=AuthTktAuthenticationPolicy):
    """Set up authentication and authorization policies.

    ``_auth_policy`` is only used for tests.
    """
    authz_policy = AuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    timeout = settings['yait.auth.timeout']
    if timeout == '0':
        timeout = None
        reissue_time = None
    else:
        timeout = int(timeout)
        reissue_time = timeout / 10
    secure_only = settings['yait.auth.secure_only'].lower() in ('true', 'yes')
    auth_policy = _auth_policy(
        secret=settings['yait.auth.secret'],
        secure=secure_only,
        timeout=timeout,
        reissue_time=reissue_time)
    config.set_authentication_policy(auth_policy)


def make_app(global_settings, **settings):
    """Set up and return the WSGI application."""
    config = Configurator(settings=settings)
    db_verbose = settings.get('yait.db_verbose', 'false').lower() == 'true'
    initialize_sql(settings['yait.db_url'], echo=db_verbose)

    # Request properties
    config.set_request_property('yait.auth._get_user', name='user', reify=True)
    config.set_request_property('yait.cache.cache', name='cache', reify=True)

    # Authentication and authorization policies
    _set_auth_policies(config, settings)

    # Session
    session_secret = settings['yait.session.secret']
    session_factory = UnencryptedCookieSessionFactoryConfig(session_secret)
    config.set_session_factory(session_factory)

    # Cache
    cache_region = dogpile.cache.make_region()
    cache_region.configure('dogpile.cache.memory')
    register_cache_region(config.registry, cache_region)

    # Routes and views:
    # - site / general purpose views / login / static assets
    config.add_static_view('static', 'static')
    config.add_route('home', '/')
    config.add_view('.views.site.home', route_name='home',
                    renderer='templates/home.pt')
    config.add_route('login', '/login')
    config.add_view('.views.auth.login_form', route_name='login',
                    request_method='GET',
                    renderer='templates/login.pt')
    config.add_view('.views.auth.login', route_name='login',
                    request_method='POST',
                    renderer='templates/login.pt')
    config.add_route('logout', '/logout')
    config.add_view('.views.auth.logout', route_name='logout')
    config.add_route('preferences', '/preferences')
    config.add_view('.views.preferences.prefs', route_name='preferences',
                    renderer='templates/preferences.pt')

    # - control panel
    config.add_route('control_panel', '/control-panel')
    config.add_view('.views.manage.control_panel', route_name='control_panel',
                    renderer='templates/control_panel.pt')
    config.add_route('users', '/control-panel/users')
    config.add_view('.views.manage.list_users', route_name='users',
                    renderer='users.pt')
    config.add_route('user_add', '/control-panel/user/add')
    config.add_view('.views.manage.add_user_form', route_name='user_add',
                    request_method='GET',
                    renderer='templates/user_add.pt')
    config.add_view('.views.manage.add_user', route_name='user_add',
                    request_method='POST',
                    renderer='templates/user_add.pt')
    config.add_route('user_edit', '/control-panel/user/{user_id}/edit')
    config.add_view('.views.manage.edit_user_form', route_name='user_edit',
                    request_method='GET',
                    renderer='templates/user_edit.pt')
    config.add_view('.views.manage.edit_user', route_name='user_edit',
                    request_method='POST')
    config.add_route('user_roles', '/control-panel/user/{user_id}/roles')
    config.add_view('.views.manage.list_user_roles', route_name='user_roles',
                    renderer='templates/user_roles.pt')
    config.add_route('projects', '/control-panel/projects')
    config.add_view('.views.manage.list_projects', route_name='projects',
                    renderer='templates/projects.pt')
    config.add_route('project_add', '/control-panel/add-project')
    config.add_view('.views.manage.add_project_form', route_name='project_add',
                    request_method='GET',
                    renderer='templates/project_add.pt')
    config.add_view('.views.manage.add_project', route_name='project_add',
                    request_method='POST',
                    renderer='templates/project_add.pt')
    config.add_route('project_delete', '/control-panel/delete-project')
    config.add_view('.views.manage.delete_project',
                    route_name='project_delete', request_method='POST')

    # - projects
    config.add_route('project_home', '/p/{project_name}')
    config.add_view('.views.project.home', route_name='project_home',
                    renderer='templates/project.pt')
    config.add_route('project_configure', '/p/{project_name}/configure')
    config.add_view('.views.project.configure_form',
                    route_name='project_configure',
                    request_method='GET',
                    renderer='templates/project_configure.pt')
    config.add_view('.views.project.configure',
                    route_name='project_configure',
                    request_method='POST',
                    renderer='templates/project_configure.pt')
    config.add_route('project_configure_roles',
                     '/p/{project_name}/configure-roles')
    config.add_view('.views.project.configure_roles_form',
                    route_name='project_configure_roles',
                    request_method='GET',
                    renderer='templates/project_roles.pt')
    config.add_view('.views.project.configure_roles',
                    route_name='project_configure_roles',
                    request_method='POST',
                    renderer='templates/project_roles.pt')
    config.add_route('project_configure_statuses',
                     '/p/{project_name}/configure-statuses')
    config.add_view('.views.project.configure_statuses_form',
                    route_name='project_configure_statuses',
                    request_method='GET',
                    renderer='templates/project_statuses.pt')
    config.add_view('.views.project.configure_statuses',
                    route_name='project_configure_statuses',
                    request_method='POST',
                    renderer='templates/project_statuses.pt')
    config.add_route('project_issues',
                     '/p/{project_name}/issues')
    config.add_view('.views.project.issues',
                    route_name='project_issues',
                    renderer='templates/project_issues.pt')
    config.add_route('project_recent_activity',
                     '/p/{project_name}/recent-activity')
    config.add_view('.views.project.recent_activity',
                    route_name='project_recent_activity',
                    renderer='templates/project_recent_activity.pt')
    config.add_route('project_search', '/p/{project_name}/search')
    config.add_view('.views.project.search_form', route_name='project_search')

    # - issues
    config.add_route('issue_add', '/p/{project_name}/add')
    config.add_view('.views.issue.add_form', route_name='issue_add',
                    request_method='GET',
                    renderer='templates/issue_add.pt')
    config.add_view('.views.issue.add', route_name='issue_add',
                    request_method='POST',
                    renderer='templates/issue_add.pt')
    config.add_route('ajax_render_text', '/ajax-render-text')
    config.add_view('.views.issue.ajax_render_text',
                    route_name='ajax_render_text',
                    renderer='json')
    config.add_route('issue_view', '/p/{project_name}/{issue_ref}')
    config.add_view('.views.issue.view', route_name='issue_view',
                    renderer='templates/issue.pt')
    config.add_route('issue_update', '/p/{project_name}/{issue_ref}/update')
    config.add_view('.views.issue.update', route_name='issue_update',
                    request_method='POST',
                    renderer='templates/issue.pt')

    # - not found and forbidden
    config.add_notfound_view('.views.site.not_found',
                             renderer='templates/notfound.pt')
    config.add_forbidden_view('.views.auth.forbidden',
                              renderer='templates/forbidden.pt')

    # Internationalization
    config.add_translation_dirs('yait:locale')
    config.set_locale_negotiator('yait.i18n.locale_negotiator')

    return config.make_wsgi_app()
