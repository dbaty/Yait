from unittest import TestCase


class TestRestRenderer(TestCase):

    def _call_fut(self, text):
        from yait.text import render_rest
        return render_rest(text)

    def test_basics(self):
        text = u'this is **bold**'
        expected = u'<p>this is <strong>bold</strong></p>'
        self.assertEqual(self._call_fut(text), expected)


class TestPlainTextRenderer(TestCase):

    def _call_fut(self, text):
        from yait.text import render_plain
        return render_plain(text)

    def test_paragraphs_and_newlines(self):
        text = '\r\n'.join(('This is a test.',
                            'I am a new line.',
                            '',
                            'I am the second paragraph.'))
        expected = ('<p>This is a test.<br/>I am a new line.</p>'
                    '<p>I am the second paragraph.</p>')
        self.assertEqual(self._call_fut(text), expected)
