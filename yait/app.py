from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound

from yait.auth import AuthorizationPolicy
from yait.models import initialize_sql


def _set_auth_policies(config, settings,
                       _auth_policy=AuthTktAuthenticationPolicy):
    """Set up authentication and authorization policies.

    ``_auth_policy`` is only used for tests.
    """
    authz_policy = AuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    reissue_time = int(settings['yait.auth.timeout']) / 10
    secure_only = settings['yait.auth.secure_only'].lower() in ('true', 'yes')
    auth_policy = _auth_policy(
        secret=settings['yait.auth.secret'],
        secure=secure_only,
        timeout=int(settings['yait.auth.timeout']),
        reissue_time=int(reissue_time))
    config.set_authentication_policy(auth_policy)

def make_app(global_settings, **settings):
    """Set up and return the WSGI application."""
    config = Configurator(settings=settings)
    db_verbose = settings.get('yait.db_verbose', 'false').lower() == 'true'
    initialize_sql(settings['yait.db_url'], echo=db_verbose)

    # Request properties
    config.set_request_property('yait.auth._get_user', name='user', reify=True)

    # Authentication and authorization policies
    _set_auth_policies(config, settings)

    # FIXME: how to have internal routes ('control-panel', 'search',
    # etc.) not conflict with future project names: "/meta/<route>",
    # "/_/<route>", "_<route>", or rather use a specific prefix for
    # projects ('/p/<project_name>') and possibly users too
    # ('/u/<login>')?

    # Regular views:
    #   - site / general purpose views / static assets
    config.add_static_view('static', 'static')
    config.add_route('home', '/')
    config.add_view('yait.views.site.home', route_name='home')
    #   - global admin
    config.add_route('control_panel', '/control-panel')
    config.add_view('.views.manage.control_panel', route_name='control_panel')
    config.add_route('admins', '/control-panel/admins')
    config.add_view('.views.manage.list_admins', route_name='admins')
    config.add_route('admins_add', '/control-panel/add-admin')
    config.add_view('.views.manage.add_admin', route_name='admins_add',
                    request_method='POST')
    config.add_route('admins_delete', '/control-panel/delete-admin')
    config.add_view('.views.manage.delete_admin', route_name='admins_delete',
                    request_method='POST')
    config.add_route('projects', '/control-panel/projects')
    config.add_view('.views.manage.list_projects', route_name='projects')
    config.add_route('projects_del', '/control-panel/delete-project')
    config.add_view('.views.manage.delete_project', route_name='projects_del',
                    request_method='POST')
    #  - projects
    # FIXME: should be move under the 'issues' section, but has to be
    # defined before the 'project_home' route, otherwise it will never
    # be picked up. This problem may be lifted if we add a prefix to
    # such global views (see FIXME above).
    config.add_route('ajax_render_text', '/ajax-render-text')
    config.add_view('.views.issue.ajax_render_text',
                    route_name='ajax_render_text', renderer='json')
    config.add_route('add_project', '/add-project')
    config.add_view('.views.project.add_project_form',
                    route_name='add_project', request_method='GET')
    config.add_view('.views.project.add_project',
                    route_name='add_project', request_method='POST')
    config.add_route('project_home', '/{project_name}')
    config.add_view('.views.project.project_home', route_name='project_home')
    #  - issues
    config.add_route('add_issue', '/{project_name}/add-issue')
    config.add_view('.views.issue.add_issue_form', route_name='add_issue',
                    request_method='GET')
    config.add_view('.views.issue.add_issue', route_name='add_issue',
                    request_method='POST')
    config.add_route('issue_view', '/{project_name}/{issue_ref}')
    config.add_view('.views.issue.issue_view', route_name='issue_view')
    config.add_route('issue_update', '/{project_name}/{issue_ref}/update')
    config.add_view('.views.issue.issue_update', route_name='issue_update',
                    request_method='POST')
    # Special views
    #   - not found
    config.add_view('.views.site.not_found', context=HTTPNotFound)

    # Internationalization
    config.add_translation_dirs('yait:locale')
    config.set_locale_negotiator('yait.i18n.locale_negotiator')

    return config.make_wsgi_app()
