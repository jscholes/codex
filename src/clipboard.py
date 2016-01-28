# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.

import wx


class ClipboardError(Exception):
    pass


class NoFilesOnClipboardError(Exception):
    pass


class SetClipboardDataError(Exception):
    pass


def get_files_from_clipboard():
    clipboard = get_opened_clipboard()
    file_data_object = create_file_data_object()
    if check_for_files_on_clipboard(clipboard):
        store_clipboard_data_in_object(clipboard, file_data_object)
        flush_clipboard(clipboard)
        close_clipboard(clipboard)
        return get_filenames_from_object(file_data_object)
    else:
        raise NoFilesOnClipboardError


def put_files_on_clipboard(path_list):
    clipboard = get_opened_clipboard()
    file_data_object = create_file_data_object()
    add_paths_to_file_data_object(path_list, file_data_object)
    store_object_data_on_clipboard(file_data_object, clipboard)
    flush_clipboard(clipboard)
    close_clipboard(clipboard)


def get_opened_clipboard():
    if wx.TheClipboard.Open():
        return wx.TheClipboard
    else:
        raise ClipboardError


def create_file_data_object():
    return wx.FileDataObject()


def add_paths_to_file_data_object(path_list, file_data_object):
    for path in path_list:
        file_data_object.AddFile(path)


def check_for_files_on_clipboard(clipboard):
    filename_format = create_data_format(wx.DF_FILENAME)
    return clipboard.IsSupported(filename_format)


def create_data_format(identifier):
    return wx.DataFormat(identifier)


def store_clipboard_data_in_object(clipboard, object):
    clipboard.GetData(object)


def store_object_data_on_clipboard(data_object, clipboard):
    if not clipboard.SetData(data_object):
        raise SetClipboardDataError


def get_filenames_from_object(object):
    return object.GetFilenames()


def flush_clipboard(clipboard):
    clipboard.Flush()


def close_clipboard(clipboard):
    clipboard.Close()

