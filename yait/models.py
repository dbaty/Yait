from cryptacular.bcrypt import BCRYPTPasswordManager

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import PickleType
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Table
from sqlalchemy import Unicode
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from yait.text import render
from yait.utils import time_to_str


## Be careful here if you change these values. The value is supposed
## (in several places in the code) to be 1 + CONSTANT.index(value)
## For example:
##     u'bug' == ISSUE_KIND_LABELS[ISSUE_KIND_BUG - 1]
ISSUE_KIND_BUG = 1
ISSUE_KIND_IMPROVEMENT = 2
ISSUE_KIND_TASK = 3
ISSUE_KIND_QUESTION = 4
ISSUE_KIND_VALUES = (ISSUE_KIND_BUG,
                     ISSUE_KIND_IMPROVEMENT,
                     ISSUE_KIND_TASK,
                     ISSUE_KIND_QUESTION)
ISSUE_KIND_LABELS = (u'bug', u'improvement', u'task', u'question')
DEFAULT_ISSUE_KIND = ISSUE_KIND_BUG

## Same warning as for ISSUE_KIND_*
ISSUE_PRIORITY_LOW = 1
ISSUE_PRIORITY_MEDIUM = 2
ISSUE_PRIORITY_HIGH = 3
ISSUE_PRIORITY_CRITICAL = 4
ISSUE_PRIORITY_VALUES = (ISSUE_PRIORITY_LOW,
                         ISSUE_PRIORITY_MEDIUM,
                         ISSUE_PRIORITY_HIGH,
                         ISSUE_PRIORITY_CRITICAL)
ISSUE_PRIORITY_LABELS = (u'low', u'medium', u'high', u'critical')
DEFAULT_ISSUE_PRIORITY = ISSUE_PRIORITY_MEDIUM

ISSUE_STATUS_OPEN = u'open'
ISSUE_STATUS_PARENT = u'parent'
ISSUE_STATUS_VALUES = (ISSUE_STATUS_OPEN,
                       ISSUE_STATUS_PARENT,
                       u'in progress',
                       u'on hold',
                       u'completed')
DEFAULT_ISSUE_STATUS = ISSUE_STATUS_OPEN

RELATIONSHIP_KINDS = (u'is child of',
                      u'is blocked by')


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
metadata = MetaData()

class Model(object):
    def __init__(self, **kwargs):
        # FIXME: not needed. Remove checks (but keep setattr!).
        # We check that the attributes we want to initialize are
        # indeed columns of the table. It helps avoiding typos.
        allowed = dir(self)
        for attr, value in kwargs.items():
            if attr not in allowed:
                raise AttributeError(
                    'Initializing "%s" with the "%s" unknown attribute.' % (
                        self.__class__, attr))
            setattr(self, attr, value)


class Project(Model):

    def __repr__(self):
        return '<Project %s (id=%d)>' % (self.name, self.id)

## FIXME: shall we use String (VARCHAR) or Text?
## FIXME: add NOT NULL constraints
## FIXME: add UNIQUE constraints
## FIXME: add indexes
projects_table = Table(
    'projects',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False, unique=True),
    Column('title', Unicode, nullable=False),
    Column('public', Boolean, nullable=False))


class Issue(Model):
    _ordered = (
        ## List of attributes ordered as they should appear in
        ## comments details.
        ('title', 'title'),
        ('kind', 'kind'),
        ('priority', 'priority'),
        ('status', 'status'),
        ('resolution', 'resolution'),
        ('assignee', 'assignee'),
        ('deadline', 'deadline'),
        ('time_estimated', 'estimated'),
        ('time_billed', 'billed'),
        ('time_spent_real', 'spent (real)'),
        ('time_spent_public', 'spent (public)'),
        )

    def __repr__(self):
        return '<Issue %d (id=%d, project=%d)>' % (
            self.ref, self.id, self.project_id)

    def get_kind(self):
        return ISSUE_KIND_LABELS[self.kind - 1]

    def get_priority(self):
        return ISSUE_PRIORITY_LABELS[self.priority - 1]

    def get_parent(self):
        pass ## FIXME

    def get_children(self):
        pass ## FIXME

    def get_blocked_by(self):
        pass ## FIXME

    def get_blocking(self):
        pass ## FIXME

    def get_time_info(self, include_private_info):
        """Return a dictionary of time-related information for this
        issue:

        - ``billed``

        - ``estimated``

        - ``spent_real``: sum of the (real) time spent in all
          changes;

        - ``spent_public``: sum of the (public) time spent in all
          changes.

        ``estimated`` and ``spent_public`` are included only if
        ``include_private_info`` is enabled.

        All time information is converted to the "1w 2d 3h" format.
        """
        data = {'billed': self.time_billed or 0,
                'spent_public': 0}
        if include_private_info:
            data.update(estimated=self.time_estimated or 0)
            data.update(spent_real=0)
        for change in self.changes:
            data['spent_public'] += change.time_spent_public or 0
            if include_private_info:
                data['spent_real'] += change.time_spent_real or 0
        for key, value in data.items():
            data[key] = time_to_str(value)
        return data

issues_table = Table(
    'issues',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('ref', Integer),
    Column('title', Unicode),
    Column('reporter', Unicode),
    Column('assignee', Unicode),
    Column('kind', Integer), ## FIXME: could be an Enum
    Column('priority', Integer), ## FIXME: could be an Enum
    Column('status', Unicode),
    ## FIXME: is 'resolution' useful?
    ## Update 1: Yes, it's useful.
    ## Update2: ok, perhaps it's useful, but there is no UI
    ## yet. Proposal: when the user selects the 'close' status, the
    ## resolution field shows up. Otherwise, it is hidden (and
    ## ignored in the form controller).
    Column('resolution', Unicode),
    Column('date_created', DateTime),
    Column('date_edited', DateTime),
    Column('date_closed', DateTime),
    Column('deadline', DateTime),
    Column('time_estimated', Integer),
    Column('time_billed', Integer))


class Change(Model):

    def __repr__(self):
        return '<Change %d (issue=%d)>' % (self.id, self.issue_id)

    def get_rendered_text(self):
        return render(self.text, self.text_renderer)

    def get_details(self, include_private_time_info=False):
        """Return a list of changes as mappings."""
        details = []
        for attr, label in Issue._ordered:
            if attr in ('time_estimated', 'time_spent_real') and \
                    not include_private_time_info:
                continue
            try:
                before, after = self.changes[attr]
            except KeyError:
                continue
            ## FIXME: the code below is verbose. Could we not do better?
            if not before:
                before = 'none'
            else:
                if attr.startswith('time_'):
                    before = time_to_str(before)
                elif attr == 'kind':
                    before = ISSUE_KIND_LABELS[before - 1]
                elif attr == 'priority':
                    before = ISSUE_PRIORITY_LABELS[before - 1]
            if not after:
                after = 'none'
            else:
                if attr.startswith('time_'):
                    after = time_to_str(after)
                elif attr == 'kind':
                    after = ISSUE_KIND_LABELS[after - 1]
                elif attr == 'priority':
                    after = ISSUE_PRIORITY_LABELS[after - 1]
            details.append({'attr': attr, 'label': label,
                            'before': before, 'after': after})
        return details


changes_table = Table(
    'changes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('issue_id', Integer, ForeignKey('issues.id')),
    Column('author', Integer, ForeignKey('users.id')),
    Column('date', DateTime),
    Column('time_spent_real', Integer),
    Column('time_spent_public', Integer),
    Column('text', Text),
    Column('text_renderer', String(20)),
    Column('changes', PickleType(mutable=False))) ## FIXME: I think that we do need it to be mutable. To be checked.


class IssueRelationship(Model):
    pass

issue_relationships_table = Table(
    'issue_relationships',
    metadata,
    Column('source_id', Integer, ForeignKey('issues.id')),
    Column('target_id', Integer, ForeignKey('issues.id')),
    Column('kind', Integer)) ## FIXME: could be an Enum


class Role(Model):
    pass

roles_table = Table(
    'roles',
    metadata,
    ## FIXME: add a constraint: the triple should be unique.
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('role', Integer)) ## FIXME: could be an Enum



_pwd_manager = BCRYPTPasswordManager()

class User(Model):
    def _get_password(self):
        return self._password

    def _set_password(self, plaintext):
        self._password = _pwd_manager.encode(plaintext)

    password = property(_get_password, _set_password)

    def validate_password(self, plaintext):
        return _pwd_manager.check(self.password, plaintext)

users_table = Table(
    'users',
    metadata,
    # FIXME: add constraints
    Column('id', Integer, primary_key=True),
    Column('login', Unicode, nullable=False, unique=True),
    Column('password', String(80), nullable=False),
    Column('fullname', Unicode(80), nullable=False),
    Column('email', Unicode, nullable=False),
    Column('is_admin', Boolean, nullable=False))
#####################################################################



#####################################################################
## Mappers
##########
projects_mapper = mapper(
    Project, projects_table,
    properties={'issues': relationship(Issue, lazy='select')})
issues_mapper = mapper(
    Issue, issues_table,
    properties={'changes': relationship(Change, lazy='select')})
changes_mapper = mapper(Change, changes_table)
issue_relationships_mapper = mapper(
    IssueRelationship, issue_relationships_table,
    primary_key=(issue_relationships_table.c.source_id,
                 issue_relationships_table.c.target_id,
                 issue_relationships_table.c.kind))
roles_mapper = mapper(
    Role, roles_table,
    primary_key=(roles_table.c.user_id, roles_table.c.project_id))
users_mapper = mapper(User, users_table)
#####################################################################



#####################################################################
## Initialization
#################
def initialize_sql(db_string, echo=False):
    engine = create_engine(db_string, echo=echo)
    DBSession.configure(bind=engine)
    metadata.bind = engine
    metadata.create_all(engine)
    return engine
