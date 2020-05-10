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

import datetime
import logging
from pathlib import Path
import zipfile

from gi.repository import Gtk


DATE_FORMAT = '%Y-%m-%d'
MAX_BACKUP_AGE = 7
BACKUP_NOW = 100
ASK_NEXT_TIME = 200
NEVER_ASK_AGAIN = 300


class Archiver:
    def __init__(self, journal):
        self.journal = journal

    def check_last_backup_date(self):
        if not self._backup_necessary():
            return

        logging.warning('Last backup is older than %d days.' % MAX_BACKUP_AGE)
        text1 = _('It has been a while since you made your last backup.')
        text2 = _('You can backup your journal to a zip file to avoid data loss.')
        dialog = Gtk.MessageDialog(
            parent=self.journal.frame.main_frame,
            type=Gtk.MessageType.QUESTION,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_format=text1)
        dialog.set_title(_('Backup'))
        dialog.format_secondary_text(text2)
        dialog.add_buttons(
            _('Backup now'), BACKUP_NOW,
            _('Ask at next start'), ASK_NEXT_TIME,
            _('Never ask again'), NEVER_ASK_AGAIN)

        answer = dialog.run()
        dialog.hide()
        if answer == BACKUP_NOW:
            self.backup()
        elif answer == ASK_NEXT_TIME:
            pass
        elif answer == NEVER_ASK_AGAIN:
            self.journal.config['lastBackupDate'] = datetime.datetime.max.strftime(DATE_FORMAT)

    def backup(self):
        def write_archive(archive_file_name, files):
            archive = zipfile.ZipFile(archive_file_name, mode="w", compression=zipfile.ZIP_DEFLATED)
            for file in files:
                archive.write(file, file.name)
            archive.close()

        backup_file = self._get_backup_file()
        # Abort if user did not select a path.
        if not backup_file:
            return

        self.journal.save_to_disk()
        data_dir = self.journal.dirs.data_dir
        archive_files = []
        for file in data_dir.rglob('*'):
            filename = str(file)
            if not filename.endswith('~') and 'RedNotebook-Backup' not in filename:
                archive_files.append(file)

        write_archive(backup_file, archive_files)

        logging.info('The content has been backed up at %s' % backup_file)
        self.journal.config['lastBackupDate'] = datetime.datetime.now().strftime(DATE_FORMAT)
        self.journal.config['lastBackupDir'] = str(backup_file.parent)

    def _backup_necessary(self):
        now = datetime.datetime.now()
        date_string = self.journal.config.read('lastBackupDate', now.strftime(DATE_FORMAT))
        try:
            last_backup_date = datetime.datetime.strptime(date_string, DATE_FORMAT)
        except ValueError as err:
            logging.error('Last backup date could not be read: %s' % err)
            return True
        last_backup_age = (now - last_backup_date).days
        logging.info('Last backup was made %d days ago' % last_backup_age)
        return last_backup_age > MAX_BACKUP_AGE

    def _get_backup_file(self) -> Path:
        if self.journal.title == 'data':
            name = ''
        else:
            name = '-' + self.journal.title

        proposed_filename = 'RedNotebook-Backup{}-{}.zip'.format(name, datetime.date.today())
        proposed_directory = self.journal.config.read('lastBackupDir', Path.home())

        backup_dialog = self.journal.frame.builder.get_object('backup_dialog')
        backup_dialog.set_transient_for(self.journal.frame.main_frame)
        backup_dialog.set_current_folder(str(proposed_directory))
        backup_dialog.set_current_name(proposed_filename)

        filter = Gtk.FileFilter()
        filter.set_name("Zip")
        filter.add_pattern("*.zip")
        backup_dialog.add_filter(filter)

        response = backup_dialog.run()
        backup_dialog.hide()

        if response == Gtk.ResponseType.OK:
            path = Path(backup_dialog.get_filename())
            return path
