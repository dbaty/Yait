"""Custom plugins for ``repoze.who``.

FIXME: the 'flatten' patch is being backported upstream to
'repoze.who.plugins.ldap'.

$Id$
"""

import ldap

from repoze.lru import LRUCache

from repoze.who.plugins.ldap import LDAPAttributesPlugin as Base
from repoze.who.plugins.ldap.plugins import make_ldap_connection


metadata_cache = LRUCache(100)

class LDAPAttributesPlugin(Base):
    """A derived version of the ``repoze.who.plugins.ldap`` plugin that:

    - caches metadata so that we do not hammer the LDAP server to
      retrieve information that is unlikely to change (and even if it
      changes, we do not really care);

    - may flatten attributes (that would come as single-valued list
      otherwise).
    """

    def __init__(self, ldap_connection, attributes=None,
                 filterstr='(objectClass=*)',
                 flatten_attributes=()):
        """
        Fetch LDAP attributes of the authenticated user.
        
        @param ldap_connection: The LDAP connection to use to fetch this data.
        @type ldap_connection: C{ldap.ldapobject.SimpleLDAPObject} or C{str}
        @param attributes: The authenticated user's LDAP attributes you want to
            use in your application; an interable or a comma-separate list of
            attributes in a string, or C{None} to fetch them all.
        @type attributes: C{iterable} or C{str}
        @param filterstr: A filter for the search, as documented in U{RFC4515
            <http://www.faqs.org/rfcs/rfc4515.html>}; the results won't be
            filtered unless you define this.
        @type filterstr: C{str}
        @raise ValueError: If L{make_ldap_connection} could not create a
            connection from C{ldap_connection}, or if C{attributes} is not an
            iterable.
        @param flatten_attributes: LDAP attributes that you want to
            fetch as a string (instead of a list) when there is only
            one value. Of course, if multiple values are returned, you
            will get all of them as a list.
        @type flatten_attributes: C{iterable} or C{str}
        """
        if hasattr(attributes, 'split'):
            attributes = attributes.split(',')
        elif hasattr(attributes, '__iter__'):
            # Converted to list, just in case...
            attributes = list(attributes)
        elif attributes is not None:
            raise ValueError('The needed LDAP attributes are not valid')
        if hasattr(flatten_attributes, 'split'):
            flatten_attributes = flatten_attributes.split(',')
        elif hasattr(flatten_attributes, '__iter__'):
            # Converted to list, just in case...
            flatten_attributes = list(flatten_attributes)
        elif attributes != ():
            raise ValueError('flatten_attributes is not valid')
        self.ldap_connection = make_ldap_connection(ldap_connection)
        self.attributes = attributes
        self.filterstr = filterstr
        self.flatten_attributes = flatten_attributes


    def add_metadata(self, environ, identity):
        cache_key = identity.get('repoze.who.userid')
        metadata = metadata_cache.get(cache_key, None)
        if metadata is None:
            metadata = self.get_metadata(environ, identity)
            metadata_cache.put(cache_key, metadata)
        identity.update(metadata)


    def get_metadata(self, environ, identity):
        ## This is a copy of the original 'add_metadata()' method
        ## except that it returns the metadata instead of updating
        ## 'identity'.
        args = (identity.get('repoze.who.userid'),
                ldap.SCOPE_BASE,
                self.filterstr,
                self.attributes)
        try:
            metadata = {}
            for dn, attributes in self.ldap_connection.search_s(*args):
                for attr, value in attributes.items():
                    if attr in self.flatten_attributes and \
                            len(value) == 1:
                        attributes[attr] = value[0]
                metadata.update(attributes)
            return metadata
        except ldap.LDAPError, msg:
            environ['repoze.who.logger'].warn('Cannot add metadata: %s' % \
                                              msg)
            return None
