# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import wx

import application
import conversion

from . import dialogs


error_messages = {
    conversion.E_FILE_ALREADY_ADDED: _('File {file} has already been added.'),
    conversion.E_FILETYPE_NOT_SUPPORTED: _('Sorry, this filetype is not supported.'),
    conversion.E_FILE_NOT_FOUND: _('The specified file does not exist.')
}


def add_paths(path_list, format=None, parent=None, from_folder=False):
    valid_paths = []
    if format is None:
        options_dialog = dialogs.ConversionOptionsDialog(parent)
        result = options_dialog.ShowModal()
        if result == wx.ID_OK:
            format = options_dialog.output_format.GetClientData(options_dialog.output_format.GetSelection())
        else:
            return
    for path in path_list:
        try:
            book = conversion.add_path(path, format)
            valid_paths.append(book.input_path)
        except conversion.PathNotAddedError as e:
            if not from_folder:
                wx.MessageBox(error_messages[e.code].format(**e.kwargs), _('Error'), wx.ICON_ERROR, parent=parent)
            continue
    if parent is not None and len(valid_paths) > 0:
        application.main_window.add_conversions(valid_paths, format)
        application.main_window.refresh(    )

def start(parent=None):
    if len(conversion.conversion_queue) == 0:
        wx.MessageBox(_('No files have been added for conversion.'), _('Error'), wx.ICON_ERROR, parent=parent)
        return

    conversion_progress_dialog = dialogs.ConversionProgressDialog(parent)
    conversion_progress_dialog.ShowModal()
    conversion_progress_dialog.Destroy()
    if conversion.no_drm:
        wx.MessageBox(_('Some of the processed files were not DRM-protected.  They have been added to your output directory unmodified.'), application.title, wx.ICON_INFORMATION, parent=parent)

    if len(conversion.converted_files) == 0 and len(conversion.failed_conversions) == 0:
        cleanup()
        return

    show_conversion_complete_dialog = application.config['show_conversion_complete_dialog'] or len(conversion.failed_conversions) > 0
    if show_conversion_complete_dialog:
        conversion_complete_dialog = dialogs.ConversionCompleteDialog(parent)
        conversion_complete_dialog.ShowModal()
        conversion_complete_dialog.Destroy()
    cleanup()

def cleanup():
    conversion.stop_conversion.clear()
    conversion.skip_current_file.clear()
    conversion.conversion_queue = []
    conversion.converted_files = []
    conversion.failed_conversions = []
    conversion.remove_drm_only = False
    conversion.no_drm = False
