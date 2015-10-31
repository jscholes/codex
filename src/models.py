# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import os
import os.path
import string

import application
import conversion
from paths import make_valid_filename

class Book(object):
    def __init__(self, input_path, calibre_path=None, output_path=None, author=None, author_sort=None, title=None):
        self.input_path = input_path
        self.calibre_path = calibre_path
        self.output_path = output_path
        self.author = author
        self.author_sort = author_sort
        self.title = title

    def generate_output_path(self, extension):
        if None in (self.author, self.author_sort, self.title):
            raise ValueError('Not enough data to generate output path')

        author = make_valid_filename(self.author)
        title = make_valid_filename(self.title)

        filename_template = string.Template(application.config['filename_template'])
        # Use a trick found at https://serverfault.com/questions/232986/overcoming-maximum-file-path-length-restrictions-in-windows
        output_path = '\\\\?\\{0}.{1}'.format(os.path.join(application.config['output_directory'], filename_template.safe_substitute(author=author, title=title)), extension)

        return output_path
