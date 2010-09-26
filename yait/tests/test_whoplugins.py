"""Test plugins for ``repoze.who``.

$Id$
"""

from unittest import TestCase


class FakeLDAPConnection(object):

    def __init__(self, **attrs):
        self.error_msg = attrs.pop('error_msg', None)
        self.attrs = attrs

    def search_s(self, *args):
        if self.error_msg:
            from ldap import LDAPError
            raise LDAPError(self.error_msg)
        dn = args[0]
        return [(dn, self.attrs)]
        

class TestLDAPAttributesPlugin(TestCase):

    def _getTargetClass(self):
        from yait.whoplugins import LDAPAttributesPlugin
        return LDAPAttributesPlugin

    def _makeOne(self, **kwargs):
        ldap_connection = kwargs.pop('ldap_connection', None)
        if ldap_connection is None:
            ldap_connection = FakeLDAPConnection()
        plugin = self._getTargetClass()(ldap_connection, **kwargs)
        plugin.clear_cache()
        return plugin

    def _makeFakeLogger(self):
        class FakeLogger(object):
            def warn(self, msg):
                if not hasattr(self, 'messages'):
                    self.messages = []
                self.messages.append(msg)
        return FakeLogger()

    def test_init(self):
        plugin = self._makeOne()
        self.assert_(isinstance(plugin, self._getTargetClass()))

    def test_init_attributes_as_string(self):
        plugin = self._makeOne(attributes='cn mail')
        self.assert_(isinstance(plugin, self._getTargetClass()))

    def test_init_attributes_as_seq(self):
        plugin = self._makeOne(attributes=('cn', 'mail'))
        self.assert_(isinstance(plugin, self._getTargetClass()))

    def test_init_attributes_invalid(self):
        self.assertRaises(ValueError, self._makeOne, attributes=1)

    def test_init_flatten_attributes_as_string(self):
        plugin = self._makeOne(flatten_attributes='cn mail')
        self.assert_(isinstance(plugin, self._getTargetClass()))

    def test_init_flatten_attributes_as_seq(self):
        plugin = self._makeOne(flatten_attributes=('cn', 'mail'))
        self.assert_(isinstance(plugin, self._getTargetClass()))

    def test_init_flatten_attributes_invalid(self):
        self.assertRaises(ValueError, self._makeOne, flatten_attributes=1)

    def test_add_metadata_base(self):
        ldap_connection = FakeLDAPConnection(cn=['John Smith'])
        plugin = self._makeOne(ldap_connection=ldap_connection)
        environ = {}
        identity = {'repoze.who.userid': 'jsmith'}
        plugin.add_metadata(environ, identity)
        self.assertEqual(environ, {})
        self.assertEqual(identity['cn'], ['John Smith'])

    def test_add_metadata_flatten_attributes(self):
        ldap_connection = FakeLDAPConnection(cn=['John Smith'])
        plugin = self._makeOne(ldap_connection=ldap_connection,
                               flatten_attributes=['cn'])
        environ = {}
        identity = {'repoze.who.userid': 'jsmith'}
        plugin.add_metadata(environ, identity)
        self.assertEqual(environ, {})
        self.assertEqual(identity['cn'], 'John Smith')

    def test_add_metadata_ldap_error(self):
        ldap_connection = FakeLDAPConnection(
            error_msg='Search failed!', cn=['John Smith'])
        plugin = self._makeOne(ldap_connection=ldap_connection)
        environ = {'repoze.who.logger': self._makeFakeLogger()}
        identity = {'repoze.who.userid': 'jsmith'}
        plugin.add_metadata(environ, identity)
        self.assertEqual(environ['repoze.who.logger'].messages,
                         ['Cannot add metadata: Search failed!'])
        self.assert_('cn' not in identity)

    def test_cache(self):
        ldap_connection = FakeLDAPConnection(cn=['John Smith'])
        plugin = self._makeOne(ldap_connection=ldap_connection)
        environ = {}
        identity = {'repoze.who.userid': 'jsmith'}
        ## First call
        plugin.add_metadata(environ, identity)
        assert identity['cn'] == ['John Smith']

        ## Let's break the LDAP connection and see what happens
        ldap_connection.error_msg = 'LDAP server is down!'
        identity = {'repoze.who.userid': 'jsmith'}
        plugin.add_metadata(environ, identity)
        self.assertEqual(environ, {})
        self.assertEqual(identity['cn'], ['John Smith'])

        ## Clear cache and do it again
        plugin.clear_cache()
        environ = {'repoze.who.logger': self._makeFakeLogger()}
        identity = {'repoze.who.userid': 'jsmith'}
        plugin.add_metadata(environ, identity)
        self.assert_('cn' not in identity)
