"""Base utilities and classes for our tests.

$Id$
"""

def getTestingDBSession():
    from yait.models import DBSession
    from yait.models import initialize_sql
    initialize_sql('sqlite://')
    return DBSession
