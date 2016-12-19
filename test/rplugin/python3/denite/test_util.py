import denite.util as util


def test_convert2fuzzy_pattern():
    util.convert2fuzzy_pattern('abc') == 'a[^a]*b[^b]*c'
    util.convert2fuzzy_pattern('a/c') == 'a[^a]*/[^/]*c'


def test_convert2regex_pattern():
    util.convert2regex_pattern('def') == 'def'
    util.convert2regex_pattern('foo bar') == 'foo\|bar'
