import os
import py
import pytest

import setuptools_scm
from setuptools_scm import dump_version
from setuptools_scm import integration

from setuptools_scm.utils import data_from_mime, do


@pytest.mark.parametrize('cmd', ['ls', 'dir'])
def test_do(cmd, tmpdir):
    if not py.path.local.sysfind(cmd):
        pytest.skip(cmd + ' not found')
    do(cmd, str(tmpdir))


def test_data_from_mime(tmpdir):
    tmpfile = tmpdir.join('test.archival')
    tmpfile.write('name: test\nrevision: 1')

    res = data_from_mime(str(tmpfile))
    assert res == {
        'name': 'test',
        'revision': '1',
    }


def test_version_from_git(wd):
    wd('git init')
    wd('git config user.email test@example.com')
    wd('git config user.name "a test"')
    assert wd.version == '0.0'
    wd.write('test.txt', 'test')
    wd('git add test.txt')
    wd('git commit -m commit')

    assert wd.version.startswith('0.1.dev1+')
    assert not wd.version.endswith('1-')

    wd('git tag v0.1')
    assert wd.version == '0.1'

    wd.write('test.txt', 'test2')
    assert wd.version.startswith('0.2.dev0+')
    wd('git add test.txt')
    wd('git commit -m commit')
    assert wd.version.startswith('0.2.dev1+')
    wd('git tag version-0.2')
    assert wd.version.startswith('0.2')


def test_version_from_pkginfo(wd):
    wd.write('PKG-INFO', 'Version: 0.1')
    assert wd.version == '0.1'


def assert_root(monkeypatch, expected_root):
    """
    Patch version_from_scm to simply assert that root is expected root
    """
    def assertion(root):
        assert root == expected_root
    monkeypatch.setattr(setuptools_scm, 'version_from_scm', assertion)


def test_root_parameter_creation(monkeypatch):
    assert_root(monkeypatch, os.getcwd())
    setuptools_scm.get_version()


def test_root_parameter_pass_by(monkeypatch):
    assert_root(monkeypatch, '/tmp')
    setuptools_scm.get_version(root='/tmp')


def test_root_relative_to(monkeypatch):
    assert_root(monkeypatch, '/tmp/alt')
    __file__ = '/tmp/module/file.py'
    setuptools_scm.get_version(root='../alt', relative_to=__file__)


def test_find_files_stop_at_root_git(wd):
    wd('git init')
    wd.write('test.txt', 'test')
    wd('git add .')
    wd('git commit -m test -u test')
    wd.cwd.ensure('project/setup.cfg')
    assert integration.find_files(str(wd.cwd/'project')) == []


def test_dump_version(tmpdir):
    sp = tmpdir.strpath

    dump_version(sp, '1.0', 'first.txt')
    assert tmpdir.join('first.txt').read() == '1.0'
    dump_version(sp, '1.0', 'first.py')
    content = tmpdir.join('first.py').read()
    assert repr('1.0') in content
    import ast
    ast.parse(content)
