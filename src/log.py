# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import logging
import os
import os.path
import signal
import sys
import threading

import wx

import application

def excepthook(*exc_info):
    application.logger.critical('Unhandled exception', exc_info=exc_info)
    log_path = os.path.join(application.config_directory, '{0}.log'.format(application.internal_name))
    wx.MessageBox('An unhandled error occurred.  Please submit the log file located at {0} to the application developer.'.format(log_path), 'Error', wx.ICON_ERROR)
    os.kill(os.getpid(), signal.SIGTERM)

def add_threading_excepthook(func):
    stock_init = threading.Thread.__init__

    def init(self, *args, **kwargs):
        stock_init(self, *args, **kwargs)
        stock_run = self.run

        def run_and_catch(*run_args, **run_kwargs):
            try:
                stock_run(*run_args, **run_kwargs)
            except Exception:
                wx.CallAfter(func, *sys.exc_info())

        self.run = run_and_catch

    threading.Thread.__init__ = init

def setup():
    logger = logging.getLogger(application.internal_name)
    if application.debug:
        logger.setLevel(logging.DEBUG)
    else:
            logger.setLevel(logging.INFO)
    log_path = os.path.join(application.config_directory, '{0}.log'.format(application.internal_name))
    if os.path.exists(log_path):
        old_log = '{0}.old'.format(log_path)
        try:
            os.remove(old_log)
        except OSError as WindowsError:
            pass
        os.rename(log_path, '{0}.old'.format(log_path))
    log_file = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    log_file.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(log_file)
    application.logger = logger
    sys.excepthook = excepthook
    add_threading_excepthook(excepthook)

    if application.debug:
        application.logger.debug('Debug logging enabled')
