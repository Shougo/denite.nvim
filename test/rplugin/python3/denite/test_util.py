import denite.util as util


def test_convert2fuzzy_pattern():
    assert util.convert2fuzzy_pattern('abc') == 'a[^a]*b[^b]*c'
    assert util.convert2fuzzy_pattern('a/c') == 'a[^a]*/[^/]*c'


def test_convert2regex_pattern():
    assert util.convert2regex_pattern('def') == 'def'
    assert util.convert2regex_pattern('foo bar') == 'foo|bar'

def test_regex_convert_py_vim():
    assert util.regex_convert_py_vim(r'/foo/') == r'\v\/foo\/'
    assert util.regex_convert_py_vim(r'~foo') == r'\v\~foo'

def test_parse_jump_line():
    assert util.parse_jump_line(
        '', 'file:text') == []
    assert util.parse_jump_line(
        '', 'file:3:text') == ['file', '3', '0', 'text']
    assert util.parse_jump_line(
        '', 'file:3:4:text') == ['file', '3', '4', 'text']
