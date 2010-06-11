from repoze.bfg.configuration import Configurator


def app(global_settings, **settings):
    if settings.get('storm_verbose', '').lower() == 'true':
        import sys
        from storm.tracer import debug
        debug(True, stream=sys.stdout)
    config = Configurator(settings=settings)
    config.begin()
    config.load_zcml('configure.zcml')
    config.end()
    return config.make_wsgi_app()
