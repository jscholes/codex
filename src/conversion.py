# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
from enum import Enum
import os
import os.path
import shutil
import sys
import threading
import time
import unicodedata

import wx

import application
import calibre
import models
from paths import make_valid_filename
from signals import conversion_started, conversion_error, conversion_complete

class ConversionCancelled(Exception):
    pass

class SkipCurrentFile(Exception):
    pass

class FileAlreadyAddedError(Exception):
    pass

class FiletypeNotSupportedError(Exception):
    pass

class FileNotFoundError(Exception):
    pass

input_formats = ['azw', 'azw3', 'azw4', 'azw8', 'cbc', 'cbr', 'cbz', 'chm', 'djvu', 'docx', 'epub', 'fb2', 'html', 'htmlz', 'kfx', 'kfx-zip', 'kpf', 'lit', 'lrf', 'mobi', 'odt', 'pdb', 'pdf', 'pml', 'prc', 'rb', 'rtf', 'snb', 'tcr', 'txt', 'txtz']
untitled_formats = ['txt', 'txtz']
input_wildcards = ';'.join(['*.{0}'.format(format) for format in input_formats])

class OutputFormat(Enum):
    azw3 = 'Kindle'
    epub = 'ePub'
    docx = 'Microsoft Word 2007'
    htmlz = _('Compressed HTML')
    mobi = 'Mobipocket'
    pdf = 'PDF'
    rtf = _('Rich text format')
    txt = _('Plain text')

conversion_queue = []
converted_files = []
failed_conversions = []
output_format = 'epub'
remove_drm_only = False
no_drm = False
stop_conversion = threading.Event()
skip_current_file = threading.Event()

def filetype_not_supported(path):
    return os.path.splitext(path)[1].lstrip('.').lower() not in input_formats

def add_path(path):
    if path in [book.input_path for book in conversion_queue]:
        raise FileAlreadyAddedError
    elif filetype_not_supported(path):
        raise FiletypeNotSupportedError
    elif not os.path.exists(path):
        raise FileNotFoundError

    book = models.Book(input_path=path)
    conversion_queue.append(book)
    return book



class ConversionWorker(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ConversionWorker, self).__init__(*args, **kwargs)

    def run_command(self, cls, *args):
        '''
        Instantiates an object of the given class, which should be a subclass of calibre.BaseCommand, and waits for the command to complete while periodically checking whether the user has cancelled the conversion process.
        Upon command completion, returns the object.  If the user has cancelled the process, the command is terminated and ConversionCancelled is raised to tell the conversion worker to stop what it's doing and clean up as soon as possible.
        '''
        command = cls.__call__(*args)
        while not command.has_completed():
            time.sleep(0.1)
            if stop_conversion.is_set():
                command.cancel()
                raise ConversionCancelled
            if skip_current_file.is_set():
                command.cancel()
                raise SkipCurrentFile

        command.process_output()
        return command

    def send_signal(self, signal, **kwargs):
        wx.CallAfter(signal.send, self, **kwargs)

    def run(self, *args, **kwargs):
        for index, book in enumerate(conversion_queue):
            if stop_conversion.is_set():
                break

            try:
                self.send_signal(conversion_started, path=book.input_path, count=index + 1)
                book_id = self.run_command(calibre.CalibredbAdd, book.input_path).added_book_id
                book_info = self.run_command(calibre.CalibredbList).get_book(book_id)

                book.author = unicodedata.normalize('NFKC', book_info['authors'])
                book.author_sort = unicodedata.normalize('NFKC', book_info['author_sort'])
                book.title = unicodedata.normalize('NFKC', book_info['title'])
                book.calibre_path = book_info['formats'][0]
                if remove_drm_only:
                    book.output_path = book.generate_output_path(extension=os.path.splitext(book.calibre_path)[1].lstrip('.'))
                else:
                    book.output_path = book.generate_output_path(extension=output_format)

                base_path = os.path.dirname(book.output_path)
                if not os.path.exists(base_path):
                    os.makedirs(base_path)

                if remove_drm_only:
                    shutil.move(book.calibre_path, book.output_path)
                else:
                    self.run_command(calibre.EbookConvert, book.calibre_path, book.output_path)

                converted_files.append(book)
                calibre.reset_library_db()
            except ConversionCancelled:
                calibre.reset_library_db()
                break
            except SkipCurrentFile:
                skip_current_file.clear()
                calibre.reset_library_db()
                continue
            except calibre.InvalidCalibreOptionError:
                self.send_signal(conversion_error, error_msg=_('One or more of the custom options provided to ebook-convert.exe were not valid.  Please check your configuration.'))
                break
            except (FileNotFoundError, calibre.CommandError, calibre.DRMRemovalError) as e:
                application.logger.exception('Exception occurred while converting file: {0}'.format(book.input_path))
                failed_conversions.append(book)
                calibre.reset_library_db()
                continue
            except calibre.ExecutableNotFoundError:
                self.send_signal(conversion_error, error_msg=_('The required utilities for eBook conversion could not be found.  Please reinstall the application.'))
                break

        self.cleanup()

    def cleanup(self):
        try:
            calibre.empty_library()
        except WindowsError:
            time.sleep(0.1)
            self.cleanup()

        self.send_signal(conversion_complete)
        return
