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
    assert util.parse_jump_line(
        '', 'C:/file:3:4:text') == ['C:/file', '3', '4', 'text']

def test_parse_tag_line():
    assert util.parse_tagline(
        'name	file	/pattern/;"', '') == {
            'name': 'name', 'file': 'file',
            'pattern': 'pattern', 'line': '',
            'type': '', 'ref': '',
        }

    assert util.parse_tagline(
        'name	file	1100;"', '') == {
            'name': 'name', 'file': 'file',
            'pattern': '', 'line': '1100',
            'type': '', 'ref': '',
        }

    assert util.parse_tagline(
        'name	file	1;"	f', '') == {
            'name': 'name', 'file': 'file',
            'pattern': '', 'line': '1',
            'type': 'f', 'ref': '',
        }

    assert util.parse_tagline(
        'name	file	1;"	f	foo	bar', '') == {
            'name': 'name', 'file': 'file',
            'pattern': '', 'line': '1',
            'type': 'f', 'ref': 'foo bar',
        }

    assert util.parse_tagline(
        'name	file	/	pattern/;"', '') == {
            'name': 'name', 'file': 'file',
            'pattern': '	pattern', 'line': '',
            'type': '', 'ref': '',
        }

