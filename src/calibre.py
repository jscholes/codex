# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import codecs
import json
import os
import os.path
import re
import shlex
import shutil
import subprocess
import tempfile
import threading

import application
import conversion

class InitialisationError(Exception):
    # Raised when, for whatever reason, we can't set up the required calibre directories
    pass

class ExecutableNotFoundError(Exception):
    # Raised if a calibre executable is not found
    pass

class CommandError(Exception):
    # Raised if a command sets a return code other than 0
    pass

class DRMRemovalError(Exception):
    # Raised if the DeDRM plug-in could not decrypt a book
    pass

class InvalidCalibreOptionError(Exception):
    # Raised if the user has configured extra ebook-convert options which are not valid
    pass

book_id_re = re.compile(r'\nAdded book ids: ([0-9]+)\n')
drm_removal_error = 'Ultimately failed to decrypt'
invalid_option_error = 'error: no such option'
no_drm = 'DRM free perhaps?'
# Qt outputs a warning to stdout if we're on Windows 10
qt_warnings = [
    'Qt: Untested Windows version 10.0 detected!\n',
]

if application.is_frozen:
    calibre_path = os.path.abspath(os.path.join(application.application_path, 'calibre'))
else:
    calibre_path = os.path.abspath(os.path.join(application.application_path, os.pardir, 'calibre'))

calibre_base_path = os.path.abspath(os.path.join(application.application_path, 'calibre_base'))
calibre_config_path = os.path.join(application.config_directory, 'calibre_config')
calibre_library_path = os.path.join(application.config_directory, 'calibre_library')
calibre_temp_path = os.path.join(application.config_directory, 'calibre_temp')
calibre_cache_path = os.path.join(application.config_directory, 'calibre_cache')
calibre_database_path = os.path.join(calibre_library_path, 'metadata.db')
dedrm_plugin_path = os.path.join(calibre_base_path, 'DeDRM_plugin.zip')

calibre_paths = [
    {'base': 'calibre_config', 'path': calibre_config_path},
    {'base': 'calibre_library', 'path': calibre_library_path},
    {'base': None, 'path': calibre_cache_path},
    {'base': None, 'path': calibre_temp_path},
]

def initialise_calibre_directory(destination, base):
    source = os.path.abspath(os.path.join(calibre_base_path, base))
    try:
        application.logger.info('Copying files from: {0}'.format(source))
        shutil.copytree(source, destination)
    except shutil.Error as e:
        application.logger.exception('Error occured while initialising {0} directory'.format(base))
        raise InitialisationError

def setup_calibre_directories():
    for path in calibre_paths:
        if path['base'] == 'calibre_library':
            if not os.path.exists(calibre_library_path):
                initialise_calibre_directory(calibre_library_path, calibre_paths[1]['base'])
            else:
                empty_library()
                reset_library_db()
        else:
            if not os.path.exists(path['path']):
                if path['base'] is not None:
                    initialise_calibre_directory(path['path'], path['base'])
                else:
                    try:
                        os.makedirs(path['path'])
                    except FileExistsError:
                        pass

    application.logger.info('Calibre directories initialised successfully')

def set_calibre_environment_variables():
    os.environ['CALIBRE_CONFIG_DIRECTORY'] = calibre_config_path
    application.logger.info('Calibre config directory: {0}'.format(calibre_config_path))
    os.environ['CALIBRE_TEMP_DIR'] = calibre_temp_path
    application.logger.info('Calibre temp directory: {0}'.format(calibre_temp_path))
    os.environ['CALIBRE_CACHE_DIRECTORY'] = calibre_cache_path
    application.logger.info('Calibre cache directory: {0}'.format(calibre_cache_path))
    os.environ['CALIBRE_OVERRIDE_DATABASE_PATH'] = calibre_database_path
    application.logger.info('Calibre database path: {0}'.format(calibre_database_path))
    os.environ['CALIBRE_OVERRIDE_LANG'] = 'en'

def setup():
    setup_calibre_directories()
    set_calibre_environment_variables()
    if not os.path.exists(os.path.join(calibre_config_path, 'plugins', 'DeDRM')):
        CalibreCustomizeAddPlugin(dedrm_plugin_path)

def calibre_executable_path(name):
    return os.path.join(calibre_path, '{0}.exe'.format(name))

def reset_library_db():
    try:
        os.remove(calibre_database_path)
    except OSError as WindowsError:
        reset_library_db()

    shutil.copy(os.path.join(calibre_base_path, calibre_paths[1]['base'], 'metadata.db'), calibre_library_path)

def empty_library():
    def on_error(exc):
        raise exc

    for root, dirs, files in os.walk(calibre_library_path, topdown=False, onerror=on_error):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    shutil.copy(os.path.join(calibre_base_path, calibre_paths[1]['base'], 'metadata.db'), calibre_library_path)

def cleanup_temp_files():
    for file in os.listdir(calibre_temp_path):
        os.remove(os.path.join(calibre_temp_path, file))



class BaseCommand(object):
    def __init__(self, *args, **kwargs):
        self.returncode = None
        self.stdout = None
        self.command_args.insert(0, self.executable)
        try:
            self.buffer = tempfile.NamedTemporaryFile(dir=calibre_temp_path)
            application.logger.debug('Running command: {0}'.format(subprocess.list2cmdline(self.command_args)))
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            self.process = subprocess.Popen(self.command_args, stdout=self.buffer, stderr=subprocess.STDOUT, startupinfo=si)
        except WindowsError:
            raise ExecutableNotFoundError

    def log_error(self):
        application.logger.error('Error while running command: {0}\nReturn code: {1}\n{2}'.format(subprocess.list2cmdline(self.command_args), self.return_code, self.stdout))

    def cancel(self):
        self.process.kill()
        self.buffer.close()
        application.logger.debug('Process {0} with PID {1} terminated'.format(self.executable, self.process.pid))

    def has_completed(self):
        if self.process.poll() is not None:
            self.return_code = self.process.returncode
            self.buffer.seek(0)
            # Avoid invalid start bytes and other errors that aren't critical by using a StreamReader
            utf8_reader = codecs.getreader('utf-8')
            self.stdout = utf8_reader(self.buffer, errors='replace').read()
            self.buffer.close()

            for warning in qt_warnings:
                if warning in self.stdout:
                    application.logger.debug(r'Stripped Qt warning from output: {0}'.format(warning.strip('\n')))
                    self.stdout = self.stdout.replace(warning, '')

            application.logger.debug('Command output:\n{0}'.format(self.stdout))
            return True
        else:
            return False

    def process_output(self):
        if invalid_option_error in self.stdout:
            self.log_error()
            raise InvalidCalibreOptionError

        if self.return_code is not None and self.return_code != 0:
            self.log_error()
            raise CommandError(self.return_code)

        self._process_output()

    def _process_output(self):
        pass # Should be implemented in subclasses if required



class CalibredbAdd(BaseCommand):
    def __init__(self, path, *args, **kwargs):
        self.executable = calibre_executable_path('calibredb')
        self.path = path
        self.command_args = ['add', '--library-path', calibre_library_path, '--duplicates', self.path]
        super(CalibredbAdd, self).__init__(*args, **kwargs)

    def _process_output(self):
        # First, make sure the DRM removal didn't fail, but only if we're not converting
        # If the DRM couldn't be removed, conversion will fail anyway.  This avoids false positives on PDFs
        if drm_removal_error in self.stdout and conversion.remove_drm_only:
            self.log_error()
            raise DRMRemovalError

        if conversion.remove_drm_only and no_drm in self.stdout:
            conversion.no_drm = True

        book_id_found = book_id_re.search(self.stdout)
        if book_id_found:
            self.added_book_id = int(book_id_found.group(1))
            application.logger.debug('File {0} added to Calibre database with ID {1}'.format(self.path, self.added_book_id))
        else:
            self.log_error()
            raise CommandError



class CalibredbList(BaseCommand):
    def __init__(self, *args, **kwargs):
        self.executable = calibre_executable_path('calibredb')
        self.command_args = ['list', '--library-path', calibre_library_path, '--for-machine', '--fields', 'all']
        super(CalibredbList, self).__init__(*args, **kwargs)

    def _process_output(self):
        self.library = json.loads(self.stdout)

    def get_book(self, id):
        for book in self.library:
            if book['id'] == id:
                return book



class EbookConvert(BaseCommand):
    def __init__(self, input_path, output_path, options=None, *args, **kwargs):
        self.executable = calibre_executable_path('ebook-convert')
        self.command_args = [input_path, output_path]
        if application.config['remove_smart_punctuation']:
            self.command_args.append('--unsmarten-punctuation')
        if application.config['asciiize']:
            self.command_args.append('--asciiize')
        extra_args = application.config['extra_ebook_convert_options']
        if extra_args:
            extra_args = shlex.split(extra_args)
            self.command_args += extra_args
        super(EbookConvert, self).__init__(*args, **kwargs)



class CalibreCustomizeAddPlugin(BaseCommand):
    def __init__(self, plugin_path, *args, **kwargs):
        self.executable = calibre_executable_path('calibre-customize')
        self.command_args = ['-a', plugin_path]
        super(CalibreCustomizeAddPlugin, self).__init__(*args, **kwargs)


