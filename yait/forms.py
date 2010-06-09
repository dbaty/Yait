from wtforms.form import Form
from wtforms.fields import BooleanField
from wtforms.fields import TextField
from wtforms.validators import required
from wtforms.validators import ValidationError
from wtforms.widgets import CheckboxInput

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
from yait.utils import strToDate


class BaseForm(Form):
    """A base class for all forms in Yait."""
    pass


class AddProject(BaseForm):
    name = TextField(label=u'Name',
                     description=u'Should be short, will be part of the URL ',
                     validators=[required()]
                     )
    title = TextField(label=u'Title', validators=[required()])
    is_public = BooleanField(
        label=u'Check this box to make this project public, i.e. '
        'accessible to anonymous users. ',
        widget=CheckboxInput)

    def validate_name(self, field):
        """Make sure that the name is not already taken."""
        store = _getStore()
        if store.find(Project, name=field.data).one():
            raise ValidationError(u'This name is not available.')
        


## FIXME: remove everything below once we're done with the integration
## of WTForms.

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
                   title='',
                   is_public=False)
    required = ('name', 'title')
    convert = (('is_public', bool), )

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
               ('time_spent', strToTime),
               ('deadline', strToDate))
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


class ChangeAddForm(IssueAddForm):
    ## FIXME: the only differences with IssueAddForm are:
    ## - it has no 'title' field
    ## - 'text' field is not required
    required = ('status', )