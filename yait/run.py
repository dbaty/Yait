from repoze.bfg.configuration import Configurator


def app(global_settings, **settings):
    config = Configurator(settings=settings)
    config.begin()
    config.load_zcml('configure.zcml')
    config.end()
    return config.make_wsgi_app()
