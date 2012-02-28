from wtforms.fields import BooleanField
from wtforms.fields import DateTimeField
from wtforms.fields import SelectField
from wtforms.fields import SelectMultipleField
from wtforms.fields import TextAreaField
from wtforms.fields import TextField
from wtforms.form import Form
from wtforms.validators import optional
from wtforms.validators import required
from wtforms.validators import ValidationError
from wtforms.widgets import CheckboxInput

from yait.models import DBSession
from yait.models import DEFAULT_ISSUE_KIND
from yait.models import DEFAULT_ISSUE_PRIORITY
from yait.models import DEFAULT_ISSUE_STATUS
from yait.models import ISSUE_KIND_LABELS
from yait.models import ISSUE_KIND_VALUES
from yait.models import ISSUE_PRIORITY_LABELS
from yait.models import ISSUE_PRIORITY_VALUES
from yait.models import ISSUE_STATUS_VALUES
from yait.models import Project
from yait.utils import str_to_time
from yait.utils import time_to_str


class TimeInfoField(TextField):
    """A custom text field for time-related information."""

    def process_data(self, value):
        self.data = time_to_str(value or 0)

    def process_formdata(self, value_list):
        if value_list:
            try:
                self.data = str_to_time(value_list[0])
            except ValueError:
                self.data = value_list[0]
                raise ValueError(u'Wrong syntax.')


class BaseForm(Form):
    """A base class for all forms in Yait."""
    pass


class AddProjectForm(BaseForm):
    ## FIXME: check length of name (if we use a VARCHAR)
    ## FIXME: check length of title (if we use a VARCHAR)
    name = TextField(label=u'Name',
                     description=u'Should be short, will be part of the URL.',
                     validators=[required()])
    title = TextField(label=u'Title', validators=[required()])
    public = BooleanField(
        label=u'Make this project public, i.e. accessible to '
        'anonymous users.')

    def validate_name(self, field):
        session = DBSession()
        if session.query(Project).filter_by(name=field.data).all():
            raise ValidationError(u'This name is not available.')
        ## FIXME: check that the name contains only alphanumerical
        ## characters, underscores and dashes.


class ExtraFieldset:
    status = SelectField(
        label=u'Status',
        choices=zip(ISSUE_STATUS_VALUES, ISSUE_STATUS_VALUES),
        default=DEFAULT_ISSUE_STATUS,
        validators=[required()])
    ## FIXME: we need a specific widget and validator
    assignee = TextField(label=u'Assign issue to')
    ## FIXME: need a specific field or widget for time-related fields
    time_estimated = TimeInfoField(label=u'Estimated time (internal)')
    time_billed = TimeInfoField(label=u'Time billed')
    time_spent_real = TimeInfoField(label=u'Time spent (real, internal)')
    time_spent_public = TimeInfoField(label=u'Time spent (public)')
    deadline = DateTimeField(label='Deadline', validators=[optional()])
    priority = SelectField(
        label=u'Priority',
        coerce=int,
        choices=zip(ISSUE_PRIORITY_VALUES, ISSUE_PRIORITY_LABELS),
        default=DEFAULT_ISSUE_PRIORITY,
        validators=[required()])
    kind = SelectField(
        label=u'Kind',
        coerce=int,
        choices=zip(ISSUE_KIND_VALUES, ISSUE_KIND_LABELS),
        default=DEFAULT_ISSUE_KIND,
        validators=[required()])
    # FIXME: use an auto-complete widget
    parent = TextField(label=u'Parent issue')
    # FIXME: need work on UI
    children = SelectMultipleField(u'Child issue(s)', widget=CheckboxInput)


def text_renderer_field_factory():
    return SelectField(label=u'Text format',
                       choices=(('rest', 'reStructuredText'), ),
                       default='rest',
                       validators=[required()])


class AddIssueForm(BaseForm, ExtraFieldset):
    title = TextField(label=u'Title', validators=[required()])
    text = TextAreaField(label=u'Text', validators=[required()])
    text_renderer = text_renderer_field_factory()


class AddChangeForm(BaseForm, ExtraFieldset):
    """A form used to comment (change) an issue."""
    text = TextAreaField(label=u'Text')
    text_renderer = text_renderer_field_factory()
