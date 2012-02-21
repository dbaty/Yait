"""Test models."""


from unittest import TestCase

class TestModelConstructor(TestCase):

    def test_model_init(self):
        from yait.models import User
        User(login=u'user')

    def test_model_init_unknown_column(self):
        from yait.models import User
        self.assertRaises(AttributeError, User, foo='bar')


class TestProject(TestCase):

    def test_model_project(self):
        from yait.models import Project
        p = Project(name=u'name', title=u'Title', public=False)
        p.id = 1
        self.assertEqual(repr(p), '<Project name (id=1)>')


class TestIssue(TestCase):

    def test_model_issue(self):
        from yait.models import Issue
        i = Issue(ref=123, project_id=2)
        i.id = 1
        self.assertEqual(repr(i), '<Issue 123 (id=1, project=2)>')


class TestChange(TestCase):

    def test_model_change(self):
        from yait.models import Change
        c = Change(issue_id=2)
        c.id = 1
        self.assertEqual(repr(c), '<Change 1 (issue=2)>')


class TestIssueRelationship(TestCase):

    ## FIXME: enable later
    def _test_model_issue_relationship(self):
        from yait.models import IssueRelationship
        r = IssueRelationship(source_id=1, target_id=2, kind=3)
        self.assertEqual(
            repr(r),
            '<Relationship issue 1 is blocked by issue 2>')


## FIXME: test cascade on delete
