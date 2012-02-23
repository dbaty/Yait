from unittest import TestCase


class TestRestRenderer(TestCase):

    def _call_fut(self, text):
        from yait.text import render_rest
        return render_rest(text)

    def test_basics(self):
        text = u'this is **bold**'
        expected = u'<p>this is <strong>bold</strong></p>'
        self.assertEqual(self._call_fut(text), expected)
