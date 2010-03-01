"""Initialize database.

This module is not supposed to be run directly, but rather called
through Paste with::

    paste setup-app <config-file>

$Id
"""

from storm.locals import create_database
from storm.locals import Store


## FIXME: should we replace 'DATETIME' by 'TIMESTAMP'?
## FIXME: do we really need a different schema for Sqlite and
## PostgreSQL?
## FIXME: add indexes
def initSqlite(db_string):
    database = create_database(db_string)
    store = Store(database)
    store.execute(
        'CREATE TABLE projects ('
        'id INTEGER PRIMARY KEY, '
        'name VARCHAR(25) NOT NULL UNIQUE, '
        'title VARCHAR(100) NOT NULL'
        ')'
        )
    store.execute(
        'CREATE TABLE issues ('
        'id INTEGER PRIMARY KEY, '
        'project_id INTEGER NOT NULL, '
        'ref INTEGER NOT NULL, '
        'title VARCHAR(100) NOT NULL, '
        'reporter VARCHAR(25) NOT NULL, '
        'assignee VARCHAR(25), '
        'kind INTEGER NOT NULL, '
        'priority INTEGER NOT NULL, '
        'status VARCHAR(15) NOT NULL, '
        'resolution VARCHAR(15), ' ## FIXME: useful? (cf. 'models.py')
        'date_created DATETIME NOT NULL, '
        'date_edited DATETIME, '
        'date_closed DATETIME, '
        'deadline DATETIME, '
        'time_estimated INT, '
        'time_billed INT, '
        'FOREIGN KEY (project_id) REFERENCES projects (id)'
        ')'
        )
    store.execute(
        'CREATE TABLE changes ('
        'id INTEGER PRIMARY KEY, '
        'issue_id INTEGER NOT NULL, '
        'author VARCHAR(25) NOT NULL,'
        'date DATETIME NOT NULL, '
        'time_spent INT, '
        'text TEXT, '
        'changes TEXT, '
        'FOREIGN KEY (issue_id) REFERENCES issues (id)'
        ')'
        )
    store.execute(
        'CREATE TABLE issue_relationships ('
        'source_id INTEGER, '
        'target_id INTEGER, '
        'kind INTEGER, '
        'FOREIGN KEY (source_id) REFERENCES issues (id), '
        'FOREIGN KEY (target_id) REFERENCES issues (id) '
        ')'
        )
    store.commit()
    store.close()


def initPostgreSQL():
    raise NotImplementedError ## 
    pass


def setupApp(*args, **kwargs):
    import pdb; pdb.set_trace()
    raise

    
## FIXME: ... until I make this module work with Paste.
if __name__ == '__main__':
    initSqlite('sqlite:///yait.db')
