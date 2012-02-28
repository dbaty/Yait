from unittest import TestCase


class TestStrToTime(TestCase):

    def _call_fut(self, s):
        from yait.utils import str_to_time
        return str_to_time(s)

    def test_basics(self):
        self.assertEqual(self._call_fut(''), 0)
        self.assertEqual(self._call_fut('0'), 0)
        self.assertEqual(self._call_fut('1m'), 1)
        self.assertEqual(self._call_fut('1h 25m'), 85)
        self.assertEqual(self._call_fut('1d'), 480)
        self.assertEqual(self._call_fut('1d 1h'), 540)
        self.assertEqual(self._call_fut('1d 1h 1m'), 541)
        self.assertEqual(self._call_fut('1w'), 2400)

    def test_extra_spaces(self):
        self.assertEqual(self._call_fut('  1h   1m  '), 61)

    def test_wrong_format(self):
        self.assertRaises(ValueError, self._call_fut, '1t')


class TestTimeToStr(TestCase):

    def _call_fut(self, t):
        from yait.utils import time_to_str
        return time_to_str(t)

    def test_basics(self):
        self.assertEqual(self._call_fut(0), '')
        self.assertEqual(self._call_fut(1), '1m')
        self.assertEqual(self._call_fut(59), '59m')
        self.assertEqual(self._call_fut(60), '1h')
        self.assertEqual(self._call_fut(61), '1h 1m')
        self.assertEqual(self._call_fut(479), '7h 59m')
        self.assertEqual(self._call_fut(480), '1d')
        self.assertEqual(self._call_fut(541), '1d 1h 1m')
        self.assertEqual(self._call_fut(2399), '4d 7h 59m')
        self.assertEqual(self._call_fut(2401), '1w 1m')

