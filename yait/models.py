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
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym

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

ISSUE_STATUS_OPEN = 1
ISSUE_STATUS_OPEN_LABEL = u'open'
ISSUE_STATUS_CLOSED = 2
ISSUE_STATUS_CLOSED_LABEL = u'closed'
# FIXME: do we need a default status? The default status is the first one.
DEFAULT_ISSUE_STATUS = ISSUE_STATUS_OPEN
DEFAULT_STATUSES = (
    {'id': ISSUE_STATUS_OPEN, 'label': ISSUE_STATUS_OPEN_LABEL},
    {'id': ISSUE_STATUS_CLOSED, 'label': ISSUE_STATUS_CLOSED_LABEL})

RELATIONSHIP_CHILD_OF = 1
RELATIONSHIP_PARENT_OF = -RELATIONSHIP_CHILD_OF
RELATIONSHIP_REQUIRES = 2
RELATIONSHIP_BLOCKS = -RELATIONSHIP_REQUIRES

CHANGE_TYPE_CLOSING = 1
CHANGE_TYPE_OPENING = 2
CHANGE_TYPE_REOPENING = 3
CHANGE_TYPE_UPDATE = 4
CHANGE_ACTIONS = {CHANGE_TYPE_OPENING: 'opened',
                  CHANGE_TYPE_REOPENING: 'reopened',
                  CHANGE_TYPE_UPDATE: 'updated',
                  CHANGE_TYPE_CLOSING: 'closed'}

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
metadata = MetaData()


class Model(object):
    def __init__(self, **kwargs):
        self.update(**kwargs)

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class Project(Model):

    def __repr__(self):  # FIXME: do we really need this?
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


class Status(Model):
    pass


statuses_table = Table(
    'statuses',
    metadata,
    # A composite primary key (id, project_id) is defined by the
    # mapper below.
    Column('id', Integer, nullable=False),
    Column('project_id', Integer, ForeignKey('projects.id'), nullable=False),
    Column('label', Unicode, nullable=False),
    Column('position', Integer, nullable=False))


class Issue(Model):
    _ordered = (
        # List of attributes ordered as they should appear in comment
        # details.
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
    Column('reporter', Integer, ForeignKey('users.id')),
    Column('assignee', Integer, ForeignKey('users.id')),
    # FIXME: rename 'kind' as 'type'
    Column('kind', Integer),
    Column('priority', Integer),
    Column('status', Integer),
    # FIXME: is 'resolution' useful?
    # Update 1: Yes, it's useful.
    # Update2: ok, perhaps it's useful, but there is no UI
    # yet. Proposal: when the user selects the 'close' status, the
    # resolution field shows up. Otherwise, it is hidden (and
    # ignored in the form controller).
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

    # FIXME: the code below is verbose. Could we not do better?
    def get_details(self, caches, include_private_time_info=False):
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
            if attr == 'status':
                cache = caches.statuses
            elif attr == 'assignee':
                cache = caches.fullnames
            else:
                cache = None
            if not before:
                before = 'none'
            else:
                if cache:
                    before = cache[before]
                if attr.startswith('time_'):
                    before = time_to_str(before)
                elif attr == 'kind':
                    before = ISSUE_KIND_LABELS[before - 1]
                elif attr == 'priority':
                    before = ISSUE_PRIORITY_LABELS[before - 1]
            if not after:
                after = 'none'
            else:
                if cache:
                    after = cache[after]
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
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('issue_id', Integer, ForeignKey('issues.id')),
    Column('type', Integer),  # FIXME: use an ENUM
    Column('author', Integer, ForeignKey('users.id')),
    Column('date', DateTime),
    Column('time_spent_real', Integer),
    Column('time_spent_public', Integer),
    Column('text', Text),
    Column('text_renderer', String(20)),
    # FIXME: could be a better idea to store a JSON string instead of
    # a pickle. (See
    # file:///Users/damien/data/docs/sqlalchemy/0.7.2/core/types.html#marshal-json-strings
    # and
    # file:///Users/damien/data/docs/sqlalchemy/0.7.2/orm/extensions/mutable.html#establishing-mutability-on-scalar-column-values)
    Column('changes', PickleType(mutable=False)))


class IssueRelationship(Model):
    pass

issue_relationships_table = Table(
    'issue_relationships',
    metadata,
    Column('source_id', Integer, ForeignKey('issues.id')),
    Column('target_id', Integer, ForeignKey('issues.id')),
    Column('kind', Integer))  # FIXME: should be an Enum


class Role(Model):
    pass

roles_table = Table(
    'roles',
    metadata,
    # FIXME: add a constraint: the triple should be unique.
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('project_id', Integer, ForeignKey('projects.id')),
    Column('role', Integer))  # FIXME: could be an Enum


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
    Column('password', String(60), nullable=False),
    Column('fullname', Unicode(80), nullable=False),
    Column('email', Unicode, nullable=False),
    Column('is_admin', Boolean, nullable=False))
#####################################################################


#####################################################################
## Mappers
##########
projects_mapper = mapper(
    Project, projects_table,
    # FIXME: do we really need the 'issues' relationship?
    properties={'issues': relationship(Issue, lazy='select',
                                       cascade='delete'),
                'statuses': relationship(Status, lazy='select',
                                         order_by=statuses_table.c.position,
                                         cascade='delete')})
statuses_mapper = mapper(
    Status, statuses_table,
    primary_key=(statuses_table.c.id, statuses_table.c.project_id))
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
users_mapper = mapper(
    User, users_table,
    properties={'password': synonym('_password', map_column=True)})
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
