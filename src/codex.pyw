# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import argparse
import os
import sys
import time

import accessible_output2 as ao
import wx

import application

def process_command_line():
    import conversion
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?')
    parser.add_argument('-r', '--remove-drm-only', dest='remove_drm_only', action='store_true', default=False)
    parser.add_argument('-f', '--format', nargs='?', default=application.config['default_output_format'], choices=[format.name for format in conversion.OutputFormat])

    args = parser.parse_args()
    if not args.path:
        parser.print_usage()
        parser.exit()

    application.command_line_args = args


def main():
    application.wx_app = wx.App(False)
    single_instance_checker = wx.SingleInstanceChecker()
    if single_instance_checker.IsAnotherRunning():
        wx.MessageBox('Another instance of Codex is already running.', 'Error', wx.ICON_ERROR)
        sys.exit(1)

    import paths
    paths.setup()
    import log
    log.setup()
    logger = application.logger
    logger.info('Starting application: {0}'.format(application.title))
    logger.info('Application version: {0}'.format(application.version))
    logger.info('Application directory: {0}'.format(application.application_path))
    logger.info('Application config directory: {0}'.format(application.config_directory))

    import config
    try:
        config.setup()
        log.set_debug_logging(application.config['debug'])
    except config.ConfigLoadError:
        wx.MessageBox('Unfortunately, there was a problem loading your configuration settings.  The application will now exit.', 'Configuration Error', wx.ICON_ERROR)
        sys.exit(1)

    import i18n
    i18n.setup()

    import shell_integration
    try:
        shell_integration.setup()
    except shell_integration.ShellIntegrationError:
        wx.MessageBox(_('Unfortunately there was a problem integrating Codex with Windows Explorer.  Please contact the application developer.'), _('Shell Integration Error'), wx.ICON_ERROR)
    except shell_integration.ShellIntegrationNotSupportedError:
        if 'shell_integration_not_supported' in application.config.keys():
            pass
        else:
            wx.MessageBox(_('Unfortunately, Windows Explorer integration is not currently supported on this version of Windows.'), _('Shell Integration Error'), wx.ICON_ERROR)
            application.config['shell_integration_not_supported'] = True
            application.config.write()

    import calibre
    try:
        calibre.setup()
    except calibre.InitialisationError:
        wx.MessageBox(_('Unfortunately, there was a problem initialising the configuration settings for Calibre, the tool Codex uses for eBook conversion and DRM removal.'), _('Configuration Error'), wx.ICON_ERROR)
        sys.exit(1)

    import speech
    speech.setup()

    if len(sys.argv) > 1:
        process_command_line()

    import gui
    gui.setup()
    application.wx_app.MainLoop()

if __name__ == '__main__':
    main()