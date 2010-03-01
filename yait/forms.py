from yait.models import _getStore
from yait.models import DEFAULT_ISSUE_KIND
from yait.models import DEFAULT_ISSUE_PRIORITY
from yait.models import DEFAULT_ISSUE_STATUS
from yait.models import ISSUE_KIND_LABELS
from yait.models import ISSUE_KIND_VALUES
from yait.models import ISSUE_PRIORITY_LABELS
from yait.models import ISSUE_PRIORITY_VALUES
from yait.models import ISSUE_STATUS_VALUES
from yait.models import Project
from yait.utils import strToTime

## FIXME: do we want to use an existing form lib? Do we really need
## this module at all?


class Form(object):
    values = {}
    required = ()

    def __init__(self, values=None):
        self.values = self.default.copy()
        if values:
            self.values.update(values)
        self.errors = {}

    def addError(self, field, msg):
        self.errors[field] = msg

    def validate(self):
        for field in self.required:
            if not self.values[field]:
                self.addError(field, 'This field is required.')
        return self.errors == {}

    def convertValues(self):
        for field, converter in self.convert:
            self.values[field] = converter(self.values[field])


class AddForm(Form):
    pass


class ProjectAddForm(AddForm):
    default = dict(name='',
                   title='')
    required = ('name', 'title')

    def validate(self):
        if self.values['name']:
            store = _getStore()
            if store.find(Project, name=self.values['name']).one():
                self.addError('name', 'This name is not available.')
        return AddForm.validate(self)


class IssueAddForm(AddForm):
    default = dict(
        assignee=u'',
        children=(),
        deadline=u'',
        kind=str(DEFAULT_ISSUE_KIND),
        parent=u'',
        priority=str(DEFAULT_ISSUE_PRIORITY),
        status=str(DEFAULT_ISSUE_STATUS),
        text=u'',
        time_estimated=u'',
        time_billed=u'',
        time_spent=u'',
        title=u'')
    required = ('status', 'title', 'text')
    convert = (('kind', int),
               ('priority', int),
               ('time_estimated', strToTime),
               ('time_billed', strToTime),
               ('time_spent', strToTime))
    vocab = dict(
        kind=zip(ISSUE_KIND_VALUES, ISSUE_KIND_LABELS),
        priority=zip(ISSUE_PRIORITY_VALUES, ISSUE_PRIORITY_LABELS),
        status=zip(ISSUE_STATUS_VALUES, ISSUE_STATUS_VALUES)
        )

    def validate(self):
        for attr in ('time_estimated', 'time_billed', 'time_spent'):
            if self.values[attr] and not strToTime(self.values[attr]):
                self.addError(
                    attr, 'Please provide a valid time value.')
        return AddForm.validate(self)


class ChangeAddForm(AddForm):
    default = dict(text='')
    required = ('text', )
    convert = ()

    ## FIXME
