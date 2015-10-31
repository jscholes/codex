# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import ctypes.wintypes
import os
import os.path
import string
import sys

import application

def get_user_documents_path():
    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 1
    buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buffer)

    return buffer.value

def get_user_application_data_path():
    return os.path.expandvars('%appdata%')

def setup():
    if application.is_frozen:
        application.application_path = os.path.dirname(sys.executable)
    else:
        application.application_path = os.path.dirname(os.path.abspath(__file__))
    application.user_documents_path = get_user_documents_path()
    application.config_directory = os.path.join(get_user_application_data_path(), application.internal_name)
    if not os.path.exists(application.config_directory):
        os.mkdir(application.config_directory)
    application.config_file = os.path.join(application.config_directory, '{0}.ini'.format(application.internal_name))
    application.working_path = application.user_documents_path

def walk_directory_tree(starting_path):
    files = []

    for path, directories, filenames in os.walk(starting_path, topdown=False):
        for filename in filenames:
            files.append(os.path.join(path, filename))

    return files

def make_valid_filename(filename):
    # strip out any disallowed chars and replace with underscores
    disallowed_ascii = [chr(i) for i in range(0, 32)]
    disallowed_chars = '<>:"/\\|?*^{0}'.format(''.join(disallowed_ascii))
    translator = dict((ord(char), '_') for char in disallowed_chars)
    valid_filename = filename.translate(translator).rstrip('. ')

    return valid_filename
