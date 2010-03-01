from repoze.bfg.router import make_app

def app(global_config, **settings):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    # paster app config callback
    import yait
    return make_app(None, yait, settings=settings)

