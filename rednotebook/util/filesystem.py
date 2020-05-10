# -----------------------------------------------------------------------
# Copyright (c) 2009  Jendrik Seipp
#
# RedNotebook is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# RedNotebook is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with RedNotebook; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------

import codecs
import locale
import logging
import os
from pathlib import Path
from typing import List
import platform
import subprocess
import sys

ENCODING = sys.getfilesystemencoding() or locale.getlocale()[1] or 'UTF-8'
LANGUAGE = locale.getdefaultlocale()[0]
REMOTE_PROTOCOLS = ['http', 'ftp', 'irc']

IS_WIN = sys.platform.startswith('win')
IS_MAC = (sys.platform == 'darwin')


def has_system_tray():
    return IS_WIN  # A smarter detection is needed here ;)


def main_is_frozen():
    return hasattr(sys, "frozen")


if main_is_frozen():
    app_dir = Path(sys._MEIPASS)  # os.path.dirname(sys.executable)
else:
    app_dir = Path(__file__).resolve().parent.parent

if IS_WIN:
    locale_dir = app_dir / 'share' / 'locale'
else:
    locale_dir = Path(sys.prefix) / 'share' / 'locale'

image_dir = app_dir / 'images'
frame_icon_dir = image_dir / 'rednotebook-icon'
files_dir = app_dir / 'files'

user_home_dir = Path.home()


class Filenames(dict):
    '''
    Dictionary for dirnames and filenames
    '''
    def __init__(self, config):
        for key, value in globals().items():
            # Exclude "get_main_dir()"
            if key.lower().endswith('dir') and isinstance(value, Path):
                value = value.resolve()
                self[key] = value
                setattr(self, key, value)

        self.portable = bool(config.read('portable'))

        self.journal_user_dir = self.get_user_dir(config)

        self.data_dir = self.default_data_dir

        # Assert that all dirs and files are in place so that logging can take start
        make_directories([self.journal_user_dir, self.data_dir, self.template_dir,
                          self.temp_dir])
        make_files([(self.config_file, ''), (self.log_file, '')])

        self.last_pic_dir = self.user_home_dir
        self.last_file_dir = self.user_home_dir

        self.forbidden_dirs = (user_home_dir, self.journal_user_dir)

    def get_user_dir(self, config) -> Path:
        custom = Path(config.read('userDir'))

        if custom:
            # If a custom user dir has been set,
            # ensure it is absolute
            user_dir = custom.resolve()
        else:
            if self.portable:
                user_dir = self.app_dir / 'user'
            else:
                user_dir = self.user_home_dir / '.rednotebook'

        return user_dir

    def is_valid_journal_path(self, path: Path) -> bool:
        return path.is_dir() and path.is_absolute() not in self.forbidden_dirs

    def __getattribute__(self, attr):
        user_paths = {
            'template_dir': 'templates',
            'temp_dir': 'tmp',
            'default_data_dir': 'data',
            'config_file': 'configuration.cfg',
            'log_file': 'rednotebook.log',
        }

        if attr in user_paths:
            retval = self.journal_user_dir / user_paths.get(attr)
        else:
            retval = dict.__getattribute__(self, attr)

        return retval


def read_file(filename: Path):
    """Try to read a given file.

    Return empty string if an error is encountered.
    """
    try:
        with codecs.open(str(filename), 'rb', encoding='utf-8', errors='replace') as file:
            data = file.read()
            return data
    except ValueError as err:
        logging.info(err)
    except Exception as err:
        logging.error(err)
    return ''


def write_file(filename, content):
    assert filename.is_absolute()
    try:
        with codecs.open(filename, 'wb', errors='replace', encoding='utf-8') as file:
            file.write(content)
    except OSError as e:
        logging.error(f'Error while writing to "{filename!s}": {e}')


def make_directory(dir: Path):
    if not dir.is_dir():
        dir.mkdir(parents=True)


def make_directories(dirs: List[Path]):
    for dir in dirs:
        make_directory(dir)


def make_file(file: Path, content=''):
    if not file.is_file():
        write_file(file, content)


def make_files(file_content_pairs):
    for file, content in file_content_pairs:
        make_file(file, content)


def make_file_with_dir(file: Path, content):
    make_directory(file.parent)
    make_file(file, content)


def get_relative_path(from_dir: Path, to_dir: Path):
    '''
    Try getting the relative path from from_dir to to_dir
    '''
    # If the data is saved on two different windows partitions,
    # return absolute path to to_dir.
    if from_dir.drive.upper() != to_dir.drive.upper():
        return to_dir

    return from_dir.relative_to(to_dir)


def get_journal_title(dir: Path) -> str:
    """Get Journal title
    returns the directory name or '/' if dir is '/'
    """

    # Return "/" if journal is located at /
    title = '/' if not dir.name else dir.name
    return title


def get_platform_info():
    from gi.repository import GObject
    from gi.repository import Gtk
    import yaml

    functions = [
        platform.machine, platform.platform, platform.processor,
        platform.python_version, platform.release, platform.system
    ]
    names_values = [(func.__name__, func()) for func in functions]

    names_values.extend([
        ('GTK', (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())),
        ('Glib', GObject.glib_version),
        ('PyGObject', GObject.pygobject_version),
        ('YAML', yaml.__version__),
        ])

    vals = ['{}: {}'.format(name, val) for name, val in names_values]
    return 'System info: ' + ', '.join(vals)


def system_call(args):
    '''
    Asynchronous system call

    subprocess.call runs synchronously
    '''
    subprocess.Popen(args)


def get_peak_memory_in_kb():
    try:
        # This will only work on Linux systems.
        with open("/proc/self/status") as status_file:
            for line in status_file:
                parts = line.split()
                if parts[0] == "VmPeak:":
                    return int(parts[1])
    except OSError:
        pass
    raise Warning("warning: could not determine peak memory")
