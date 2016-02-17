# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
from io import StringIO
import os.path
import sys

from configobj import ConfigObj, ConfigObjError
from validate import Validator

import application

class ConfigLoadError(Exception):
    pass

def setup():
    config_spec = StringIO('''interface_language = string(default=en)
    output_directory = string(default={default_output_directory})
    kindle_content_directory = string(default={kindle_content_directory})
    filename_template = string(default=$author\\$title)
    default_output_format = string(default=epub)
    working_directory = string(default={default_working_directory})
    show_conversion_complete_dialog = boolean(default=True)
    remove_smart_punctuation = boolean(default=False)
    asciiize = boolean(default=False)
    extra_ebook_convert_options = string(default='')'''.format(default_output_directory=os.path.join(application.user_documents_path, 'eBooks'), kindle_content_directory=os.path.join(application.user_documents_path, 'My Kindle Content'), default_working_directory=application.user_documents_path))

    try:
        config = ConfigObj(infile=application.config_file, configspec=config_spec, create_empty=True, encoding='UTF8', default_encoding='UTF8', unrepr=True)
    except ConfigObjError:
        application.logger.critical('Error loading config from: {0}'.format(application.config_file), exc_info=sys.exc_info())
        raise ConfigLoadError
        return
    application.config_validator = Validator()
    config.validate(application.config_validator, copy=True)
    config.write()
    application.config = config
    application.logger.info('Loaded configuration file: {0}'.format(application.config_file))
