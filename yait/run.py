from repoze.bfg.configuration import Configurator

from yait.models import initialize_sql


def app(global_settings, **settings):
    config = Configurator(settings=settings)
    config.begin()
    config.load_zcml()
    config.end()
    db_verbose = settings.get('db_verbose', 'false').lower() == 'true'
    initialize_sql(settings['db_string'], echo=db_verbose)
    return config.make_wsgi_app()
