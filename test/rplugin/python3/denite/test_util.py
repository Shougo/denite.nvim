import os
from unittest.mock import patch

import pytest

import denite.util as util


def test_convert2fuzzy_pattern():
    assert util.convert2fuzzy_pattern('abc') == 'a[^a]{-}b[^b]{-}c'
    assert util.convert2fuzzy_pattern('a/c') == 'a[^a]{-}/[^/]*c'


def test_convert2regex_pattern():
    assert util.convert2regex_pattern('def') == 'def'
    assert util.convert2regex_pattern('foo bar') == 'foo|bar'

def test_regex_convert_py_vim():
    assert util.regex_convert_py_vim(r'/foo/') == r'\v\/foo\/'
    assert util.regex_convert_py_vim(r'~foo') == r'\v\~foo'

def test_regex_convert_str_vim():
    assert util.regex_convert_str_vim(r'file') == 'file'

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
        'name	file	/*foo*', '') == {
            'name': 'name', 'file': 'file',
            'pattern': '\*foo\*', 'line': '',
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


@patch('denite.util.os.walk')
def test_find_rplugins_kind(walk):
    walk.side_effect = _walk_side_effect

    context = { 'runtimepath': '/a,/b' }
    source = 'kind'
    prefix = os.path.normpath('rplugin/python3/denite/%s' % source)
    loaded_paths = [os.path.normpath(x % prefix) for x in (
        '/a/%s/loaded.py', '/a/%s/bar/loaded.py', '/a/%s/bar/hoge/loaded.py',
        '/b/%s/loaded.py', '/b/%s/bar/loaded.py', '/b/%s/bar/hoge/loaded.py',
    )]

    it = util.find_rplugins(context, source, loaded_paths)
    walk.assert_not_called()

    assert next(it) == ('/a/%s/foo.py' % prefix, 'foo')
    assert next(it) == ('/a/%s/base.py' % prefix, 'base')
    assert next(it) == ('/a/%s/bar/__init__.py' % prefix, 'bar')
    assert next(it) == ('/a/%s/bar/foo.py' % prefix, 'bar.foo')
    assert next(it) == ('/a/%s/bar/base.py' % prefix, 'bar.base')
    assert next(it) == ('/a/%s/bar/hoge/__init__.py' % prefix, 'bar.hoge')
    assert next(it) == ('/a/%s/bar/hoge/foo.py' % prefix, 'bar.hoge.foo')
    assert next(it) == ('/a/%s/bar/hoge/base.py' % prefix, 'bar.hoge.base')
    walk.assert_called_once_with(
        os.path.normpath('/a/%s' % prefix),
    )
    walk.reset_mock()

    assert next(it) == ('/b/%s/foo.py' % prefix, 'foo')
    assert next(it) == ('/b/%s/base.py' % prefix, 'base')
    assert next(it) == ('/b/%s/bar/__init__.py' % prefix, 'bar')
    assert next(it) == ('/b/%s/bar/foo.py' % prefix, 'bar.foo')
    assert next(it) == ('/b/%s/bar/base.py' % prefix, 'bar.base')
    assert next(it) == ('/b/%s/bar/hoge/__init__.py' % prefix, 'bar.hoge')
    assert next(it) == ('/b/%s/bar/hoge/foo.py' % prefix, 'bar.hoge.foo')
    assert next(it) == ('/b/%s/bar/hoge/base.py' % prefix, 'bar.hoge.base')
    walk.assert_called_once_with(
        os.path.normpath('/b/%s' % prefix),
    )
    walk.reset_mock()

    with pytest.raises(StopIteration):
        next(it)
    walk.assert_not_called()


def _walk_side_effect(top, topdown=True, onerror=None, followlinks=False):
    yield (
        top,
        ['bar'],
        ['__init__.py', 'foo.py', 'base.py', 'loaded.py'],
    )
    yield (
        os.path.join(top, 'bar'),
        ['hoge'],
        ['__init__.py', 'foo.py', 'base.py', 'loaded.py'],
    )
    yield (
        os.path.join(top, 'bar', 'hoge'),
        ['hoge'],
        ['__init__.py', 'foo.py', 'base.py', 'loaded.py'],
    )
