from repoze.bfg.settings import get_settings

from storm.locals import Bool
from storm.locals import DateTime
from storm.locals import Int
from storm.locals import Pickle
from storm.locals import Reference
from storm.locals import ReferenceSet
from storm.locals import Unicode
from storm.zope.zstorm import global_zstorm

from yait.utils import renderReST
from yait.utils import timeToStr


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


def _getStore():
    """Return a Storm store."""
    return global_zstorm.get('main_db', get_settings().db_string)


class Model(object):
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class Project(Model):
    __storm_table__ = 'projects'
    id = Int(primary=True)
    name = Unicode()
    title = Unicode()
    is_public = Bool()


class Issue(Model):
    __storm_table__ = 'issues'
    id = Int(primary=True)
    project_id = Int()
    project = Reference(project_id, Project.id)
    ref = Int()
    title = Unicode()
    reporter = Unicode()
    assignee = Unicode()
    kind = Int()
    priority = Int()
    status = Unicode()
    resolution = Unicode() ## FIXME: useful? see also 'setupapp.py'. Yes, it's useful.
    date_created = DateTime()
    date_edited = DateTime()
    date_closed = DateTime()
    deadline = DateTime()
    time_estimated = Int()
    time_billed = Int()
    ## A 'changes' property is defined below after the 'Change'
    ## model. Do NOT use directly: use 'getChanges()'

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

    def getKind(self):
        return ISSUE_KIND_LABELS[self.kind - 1]

    def getPriority(self):
        return ISSUE_PRIORITY_LABELS[self.priority - 1]

    def getChanges(self):
        """Return an ordered list of changes.

        The ReferenceSet provided by Storm does not cache results.
        Thus, multiple calls to ``self.changes`` imply multiple SELECT
        calls.
        """
        if getattr(self, '_cached_changes', None) is None:
            self._cached_changes = list(self.changes)
        return self._cached_changes

    def getParent(self):
        pass ## FIXME

    def getChildren(self):
        pass ## FIXME

    def getBlockedBy(self):
        pass ## FIXME

    def getBlocking(self):
        pass ## FIXME

    def getTimeInfo(self, include_private_info):
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
        data = dict(billed=self.time_billed or 0,
                    spent_public=0)
        if include_private_info:
            data.update(estimated=self.time_estimated or 0)
            data.update(spent_real=0)
        for change in self.getChanges():
            data['spent_public'] += change.time_spent_public or 0
            if include_private_info:
                data['spent_real'] += change.time_spent_real or 0
        for key, value in data.items():
            data[key] = timeToStr(value)
        return data


class Change(Model):
    __storm_table__ = 'changes'
    id = Int(primary=True)
    issue_id = Int()
    author = Unicode()
    date = DateTime()
    time_spent_real = Int()
    time_spent_public = Int()
    text = Unicode()
    changes = Pickle()

    def getRenderedText(self):
        return renderReST(self.text)

    def getDetails(self, include_private_time_info=False):
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
                    before = timeToStr(before)
                elif attr == 'kind':
                    before = ISSUE_KIND_LABELS[before - 1]
                elif attr == 'priority':
                    before = ISSUE_PRIORITY_LABELS[before - 1]
            if not after:
                after = 'none'
            else:
                if attr.startswith('time_'):
                    after = timeToStr(after)
                elif attr == 'kind':
                    after = ISSUE_KIND_LABELS[after - 1]
                elif attr == 'priority':
                    after = ISSUE_PRIORITY_LABELS[after - 1]
            details.append(dict(attr=attr, label=label,
                                before=before, after=after))
        return details


Issue.changes = ReferenceSet(Issue.id, Change.issue_id, order_by=Change.id)


class IssueRelationship(Model):
    __storm_table__ = 'issue_relationships'
    __storm_primary__ = ('source_id', 'target_id', 'kind')
    source_id = Int()
    target_id = Int()
    kind = Int()


## FIXME: rename as Admin (table: 'admins')
class Manager(Model):
    __storm_table__ = 'managers'
    __storm_primary__ = 'user_id'
    user_id = Unicode()


class Role(Model):
    __storm_table__ = 'roles'
    __storm_primary__ = ('user_id', 'project_id')
    user_id = Unicode()
    project_id = Int()
    roles = Int()
