"""A number of properties are stored as integer identifiers in the
database but are displayed as text to the user. This includes the
status of issues, users' name, etc. Usually, we would need a JOIN on
an extra table to get the text information. To avoid that, we store
such information in memory and make it available through a ``cache``
attribute in the request (also available in the ``TemplateAPI``
instance in the templates).
"""

from zope.interface import Interface

from yait.models import DBSession
from yait.models import Status
from yait.models import User


class ICacheRegion(Interface):
    """A ``dogpile.cache`` cache region."""


def register_cache_region(registry, cache_region):
    """Register the given cache region.

    This is called from ``yait.app.make_app()``.
    """
    registry.registerUtility(cache_region, ICacheRegion)


def cache(request):
    """Allow access to the caches.

    This is a reified property that is set on the Request object.
    """
    cache_region = request.registry.getUtility(ICacheRegion)

    class CacheFacade(object):
        """Provide access to the caches.

        The following caches are provided:

        fullnames
            A dictionary that associates the id with the fullname of
            all users.

        statuses
            A dictionary that associates the id with the label of all
            statuses.
        """
        @property
        @cache_region.cache_on_arguments()
        def statuses(self):
            return dict(DBSession.query(Status.id, Status.label).all())

        @property
        @cache_region.cache_on_arguments()
        def fullnames(self):
            return dict(DBSession.query(User.id, User.fullname).all())

    return CacheFacade()
