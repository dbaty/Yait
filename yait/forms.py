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
from wtforms.widgets import PasswordInput

from yait.auth import ROLE_PROJECT_MANAGER
from yait.auth import ROLE_PROJECT_INTERNAL_PARTICIPANT
from yait.auth import ROLE_PROJECT_PARTICIPANT
from yait.i18n import _
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
from yait.models import Role
from yait.models import User
from yait.utils import str_to_time
from yait.utils import time_to_str


def int_or_none(value):
    """Coerce the given ``value`` to ``None`` if it is the empty
    string or to an integer if possible.

    This is used for selection fields that are mapped to numeric
    columns in the database, for which an empty value is accepted
    (stored as NULL in the database).
    """
    if value == '':
        return ''
    return int(value)


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
    """Form used to add a new project."""
    # FIXME: check length of name (if we use a VARCHAR)
    # FIXME: check length of title (if we use a VARCHAR)
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
        # FIXME: check that the name contains only alphanumerical
        # characters, underscores and dashes.


class ExtraFieldset:
    """A field set used both in the "add issue" and the "add comment"
    forms.
    """
    status = SelectField(
        label=u'Status',
        choices=zip(ISSUE_STATUS_VALUES, ISSUE_STATUS_VALUES),
        default=DEFAULT_ISSUE_STATUS,
        validators=[required()])
    assignee = SelectField(label=u'Assign issue to', coerce=int_or_none)
    ## FIXME: need a specific field or widget for time-related fields
    time_estimated = TimeInfoField(label=u'Estimated time (internal)')
    time_billed = TimeInfoField(label=u'Time billed')
    time_spent_real = TimeInfoField(label=u'Time spent (real, internal)')
    time_spent_public = TimeInfoField(label=u'Time spent (public)')
    deadline = DateTimeField(label='Deadline', validators=[optional()],
                             format='%Y-%m-%d %H:%M')
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
    children = SelectMultipleField(u'Child issue(s)', widget=CheckboxInput())

    def setup(self, project_id):
        self.project_id = project_id
        self.setup_choices()

    def setup_choices(self):
        choices = [('', _(u'Nobody'))]
        choices += self._get_possible_assignees()
        self.assignee.choices = choices

    def _get_possible_assignees(self):
        """Return tuples of users that are allowed to participate in
        the project.
        """
        session = DBSession()
        res = session.query(User).join(Role).filter(
            Role.project_id==self.project_id,
            Role.role.in_((ROLE_PROJECT_MANAGER,
                           ROLE_PROJECT_PARTICIPANT,
                           ROLE_PROJECT_INTERNAL_PARTICIPANT)))
        res = res.union(session.query(User).filter_by(is_admin=True))
        res = res.order_by(User.fullname)
        return [(user.id, user.fullname) for user in res]


def text_renderer_field_factory():
    return SelectField(label=u'Text format',
                       choices=(('rest', 'reStructuredText'), ),
                       default='rest',
                       validators=[required()])


class AddIssueForm(BaseForm, ExtraFieldset):
    """Form used to add a new issue."""
    title = TextField(label=u'Title', validators=[required()])
    text = TextAreaField(label=u'Text', validators=[required()])
    text_renderer = text_renderer_field_factory()


class AddChangeForm(BaseForm, ExtraFieldset):
    """Form used to comment (change) an issue."""
    text = TextAreaField(label=u'Text')
    text_renderer = text_renderer_field_factory()


class AddUserForm(BaseForm):
    """Form used to add a new user."""
    login = TextField(label=u'Login', validators=[required()])
    password = TextField(label=u'Password', widget=PasswordInput(),
                         validators=[required()])
    password_confirm = TextField(label=u'Password (confirm)',
                                 widget=PasswordInput(),
                                 validators=[required()])
    fullname = TextField(label=u'Full name', validators=[required()])
    email = TextField(label=u'E-mail address', validators=[required()])
    is_admin = BooleanField(label=u'Administrator')

    # FIXME: validate login
    # FIXME: validate password and password_confirm are equal
    # FIXME: validate fullname
    # FIXME: validate e-mail address


class EditUserForm(AddUserForm):
    """Form used to edit an existing user."""
    password = None
    password_confirm = None

    # FIXME: check that login is the current login of the user, or a
    # valid login
    # FIXME: check that e-mail address is the current address of the
    # user, of a valid e-mail.
