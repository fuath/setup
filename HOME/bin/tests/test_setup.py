import datetime
import os as os_module
import pytest
import unittest.mock as mock
from os.path import join
from unittest.mock import call, patch

import _utils

_utils.add_bin_to_path()
setup = _utils.import_executable('setup')

from lib import symlink

SOURCE_DIR = '~/setup/HOME'
ABS_SOURCE_DIR = '/Users/user/setup/HOME'
DEST_DIR = '~'
ABS_DEST_DIR = '/Users/user'


@pytest.fixture
def symlink_settings():
    return {
        'pointers': {
            'sublime_text': 'Library/Application Support/Sublime Text 3/Packages/User',
            'karabiner.xml': 'Library/Application Support/Karabiner/private.xml',
        },
        'partials': [
            '~/.config'
        ],
    }


@pytest.fixture
def partials():
    return ['/Users/user/.config']


@pytest.fixture
def actions():
    return {
        'actions': {
            'pull': {
                'func': 'repo',
                'cmd': ['pull'],
                'help': 'Pull repository from server',
                'aliases': ['update'],
            },
        }
    }


# mock everything in 'os', except use the real os.path.join and fake expanduser
@patch('lib.symlink.os', **{
    'path.join': os_module.path.join,
    'path.dirname': os_module.path.dirname,
    'path.expanduser': lambda x: x.replace('~', '/Users/user'),
})
class TestCreateSymlinks(object):
    def test_create_symlink(self, os):
        "Test that create_symlink correctly calls os.symlink"
        source_path = 'sourcepath'
        dest_path = 'destpath'

        symlink.create_symlink(source_path, dest_path)
        os.symlink.assert_called_with(source_path, dest_path)

    def test_create_symlinks_basic(self, os):
        "Test basic symlink creation. One file, no prior exists"
        symlink_settings = {}
        files = ['.bash_profile']
        os.listdir.return_value = files
        os.path.lexists.return_value = False

        with patch('lib.symlink.create_symlink') as create_symlink:
            symlink.create(symlink_settings, SOURCE_DIR, DEST_DIR)

        create_symlink.assert_called_with(
            join(ABS_SOURCE_DIR, files[0]), join(ABS_DEST_DIR, files[0]))

    def test_create_symlinks_pointers(self, os, symlink_settings):
        "Test that symlink creation correctly follows pointers"
        os.listdir.return_value = ['sublime_text']
        os.path.lexists.return_value = False

        with patch('lib.symlink.create_symlink') as create_symlink:
            symlink.create(symlink_settings, SOURCE_DIR, DEST_DIR)

        pointers = symlink_settings['pointers']
        create_symlink.assert_called_with(
            join(ABS_SOURCE_DIR, 'sublime_text'), join(ABS_DEST_DIR, pointers['sublime_text'])
        )

    def test_ignores(self, os):
        "Test that an ignored file is not symlinked"
        symlink_settings = {'ignores': ['.DS_Store']}
        os.listdir.return_value = ['.DS_Store', 'hello']
        os.path.lexists.return_value = True

        with patch('lib.symlink.create_symlink') as create_symlink:
            symlink.create(symlink_settings, SOURCE_DIR, DEST_DIR)

        create_symlink.assert_called_once_with(
            join(ABS_SOURCE_DIR, 'hello'), join(ABS_DEST_DIR, 'hello'))

    def test_create_symlinks_partials_none_existing(self, os, symlink_settings):
        "Test that symlink creation creates the intermediate directory and then symlinks the file"
        files_within_config = sorted(['myconfig', 'anotherconfig'])
        os.listdir.side_effect = [['.config'], files_within_config]
        os.path.lexists.return_value = False
        with patch('lib.symlink.create_symlink') as create_symlink:
            symlink.create(symlink_settings, SOURCE_DIR, DEST_DIR)

        os.makedirs.assert_called_with('/Users/user/.config')

        expected_calls = []
        for file in files_within_config:
            source = join(ABS_SOURCE_DIR, '.config', file)
            dest = join(ABS_DEST_DIR, '.config', file)
            expected_calls.append(call(source, dest))

        assert create_symlink.mock_calls == expected_calls

    def test_create_symlinks_partials_directory_exists(self, os, symlink_settings):
        "Test that symlink creation creates the intermediate directory and then symlinks the file"
        os.listdir.side_effect = [['.config'], ['myconfig']]
        os.path.lexists.return_value = True
        with patch('lib.symlink.create_symlink') as create_symlink:
            symlink.create(symlink_settings, SOURCE_DIR, DEST_DIR)

        os.mkdir.assert_not_called()

    def test_partial_and_pointer(self, os):
        pass

    def test_get_backup_path(self, os):
        "Test that get_backup_path correctly generates backup paths"
        original_path = '/foo/bar/baz'
        expected_path = '/foo/bar/baz.bak.20150101T010101'
        timestamp = datetime.datetime(2015, 1, 1, 1, 1, 1)

        exist_check_count = 0

        def exists(path):
            """Mimic a file-exists check"""
            nonlocal exist_check_count  # noqa
            # first time the file is checked it exists, then it's renamed and no longer exists
            exist_check_count += 1
            return exist_check_count <= 1

        os.path.exists.side_effect = exists
        with patch('lib.symlink.os', os):
            with patch('lib.symlink.datetime') as dt:
                dt.datetime.now.return_value = timestamp
                new_path = symlink.backup_file(original_path)
        assert new_path == expected_path

    def test_handle_existing_path_no_existing_file(self, os, partials):
        os.path.lexists.return_value = False  # no existing file case
        return_value = symlink.handle_existing_path(partials, 'repo_path', 'dest_path')
        # handle_existing_path returns falsy cause the symlink needs to be created
        assert bool(return_value) is False

    def test_handle_existing_path_existing_symlink_points_correctly(self, os, partials):
        os.path.lexists.return_value = True  # test what it does when file exists
        os.path.islink.return_value = True  # and is a symlink
        os.readlink.return_value = 'repo_path'  # that points to where we want

        return_value = symlink.handle_existing_path(partials, 'repo_path', 'dest_path')
        assert bool(return_value) is True  # nothing to do in this case

    def test_handle_existing_path_existing_symlink_points_incorrectly(self, os, partials):
        os.path.lexists.return_value = True  # test what it does when file exists
        os.path.islink.return_value = True  # and is a symlink
        os.readlink.return_value = 'another_path'  # this time it doesn't point where we want

        return_value = symlink.handle_existing_path(partials, 'repo_path', 'dest_path')
        os.remove.assert_called_with('dest_path')
        assert bool(return_value) is False  # need to create

    def test_handle_existing_path_existing_file_renamed(self, os, partials):
        # lastly, test the case where it's not a symlink but a real file, and test that
        # the file is renamed and that handle_existing_path returns True
        os.path.lexists.return_value = True
        os.path.islink.return_value = False
        with mock.patch('lib.symlink.backup_file') as backup_file:
            return_value = symlink.handle_existing_path(partials, 'repo_path', 'dest_path')

        assert bool(return_value) is False
        backup_file.assert_called_with('dest_path')

    def test_handle_existing_path_partial_not_backed_up(self, os, partials):
        # make sure that it's *not* backed up if it's a partial directory
        os.path.lexists.return_value = True
        os.path.islink.return_value = False
        os.path.isdir.return_value = True
        with mock.patch('lib.symlink.backup_file') as backup_file:
            return_value = symlink.handle_existing_path(
                partials, 'repo/HOME/.config', '/Users/user/.config')

        assert bool(return_value) is False
        assert not backup_file.called

    def test_handle_existing_path_regular_file(self, os, partials):
        # make sure it doesn't consider a regular file a partial and backs it up as normal
        os.path.lexists.return_value = True
        os.path.islink.return_value = False
        os.path.isdir.return_value = False
        with mock.patch('lib.symlink.backup_file') as backup_file:
            return_value = symlink.handle_existing_path(
                partials, 'repo/HOME/.config', '/Users/user/.config')

        assert bool(return_value) is False
        backup_file.assert_called_with('/Users/user/.config')


def test_follow_pointer_no_pointer(symlink_settings):
    pointers = symlink_settings['pointers']
    dest_dir = '/Users/test'

    # no pointer follow
    expected = os_module.path.join(dest_dir, 'myfile')
    actual = symlink.follow_pointer(pointers, dest_dir, 'myfile')
    assert actual == expected


def test_follow_pointer(symlink_settings):
    pointers = symlink_settings['pointers']
    dest_dir = '/Users/test'

    # pointer follow
    expected = os_module.path.join(dest_dir, pointers['sublime_text'])
    actual = symlink.follow_pointer(pointers, dest_dir, 'sublime_text')
    assert actual == expected


def test_follow_pointer_file(symlink_settings):
    pointers = symlink_settings['pointers']
    dest_dir = '/Users/test'

    # pointer follow
    expected = os_module.path.join(dest_dir, pointers['karabiner.xml'])
    actual = symlink.follow_pointer(pointers, dest_dir, 'karabiner.xml')
    assert actual == expected
