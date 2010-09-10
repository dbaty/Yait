"""Test models.

$Id$
"""

from unittest import TestCase

class TestModelConstructor(TestCase):

    def test_model_init(self):
        from yait.models import Admin
        Admin(user_id=u'admin')

    ## FIXME: enable back later. Cf. 'models.py'
    #def test_model_init_unknown_column(self):
    #    from yait.models import Admin
    #    self.assertRaises(AttributeError, Admin, **dict(foo='bar'))


## FIXME: test cascade on delete
