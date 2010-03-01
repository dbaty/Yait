from repoze.bfg.settings import get_settings

from storm.locals import DateTime
from storm.locals import Int
from storm.locals import Pickle
from storm.locals import Reference
from storm.locals import ReferenceSet
from storm.locals import Unicode

from storm.zope.zstorm import global_zstorm

from yait.utils import renderReST


## FIXME: make this configurable per project?
ISSUE_KIND_BUG = 1
ISSUE_KIND_FEATURE = 2
ISSUE_KIND_QUESTION = 3
ISSUE_KIND_TASK = 4
ISSUE_KIND_VALUES = (ISSUE_KIND_BUG,
                     ISSUE_KIND_FEATURE,
                     ISSUE_KIND_QUESTION,
                     ISSUE_KIND_TASK)
ISSUE_KIND_LABELS = (u'bug', u'feature', u'question', u'task')
DEFAULT_ISSUE_KIND = ISSUE_KIND_BUG

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
ISSUE_STATUS_VALUES = (ISSUE_STATUS_OPEN,
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
    resolution = Unicode() ## FIXME: useful? cf. 'setupapp.py'
    date_created = DateTime()
    date_edited = DateTime()
    date_closed = DateTime()
    deadline = DateTime()
    time_estimated = Int()
    time_billed = Int()
    ## A 'changes' property is defined below after the 'Change' model.

    def getKind(self):
        return ISSUE_KIND_LABELS[self.kind - 1]

    def getPriority(self):
        return ISSUE_PRIORITY_LABELS[self.priority - 1]

    def getParent(self):
        pass ## FIXME

    def getChildren(self):
        pass ## FIXME

    def getBlockedBy(self):
        pass ## FIXME

    def getBlocking(self):
        pass ## FIXME

    def getTotalTime(self):
        pass ## FIXME: return mapping of total time spent, billed and
             ## estimated for this issue and all child issues


class Change(Model):
    __storm_table__ = 'changes'
    id = Int(primary=True)
    issue_id = Int()
    author = Unicode()
    date = DateTime()
    time_spent = Int()
    text = Unicode()
    changes = Pickle()

    def getRenderedText(self):
        return renderReST(self.text)

Issue.changes = ReferenceSet(Issue.id, Change.issue_id)


class IssueRelationship(Model):
    __storm_table__ = 'issue_relationships'
    __storm_primary__ = 'source_id, target_id, kind'
    source_id = Int()
    target_id = Int()
    kind = Int()
