from unittest import TestCase
from nose.tools import eq_
from denite.util import (convert2fuzzy_pattern, convert2regex_pattern)


class UtilTestCase(TestCase):

    def test_convert2fuzzy_pattern(self):
        eq_(convert2fuzzy_pattern('abc'), 'a[^/a]*b[^/b]*c')
        eq_(convert2fuzzy_pattern('a/c'), 'a[^/a]*/[^/]*c')

    def test_convert2regex_pattern(self):
        eq_(convert2regex_pattern('def'), 'def')
        eq_(convert2regex_pattern('foo bar'), 'foo\|bar')
