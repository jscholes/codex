# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import collections

import wx

import application
import conversion


def create_button(parent, label='', callback=None, id=-1):
    control = wx.Button(parent, id=id, label=label)
    if callback and isinstance(callback, collections.Callable):
        control.Bind(wx.EVT_BUTTON, callback)

    return control


def create_labelled_field(parent, label=None, text='', read_only=False):
    control_label = wx.StaticText(parent, label=label)
    control = wx.TextCtrl(parent, -1, text)
    try:
        control.SetSizerProps(expand=True)
    except AttributeError:
        pass

    if read_only:
        control.SetWindowStyle(wx.TE_READONLY|wx.TE_NO_VSCROLL|wx.TE_MULTILINE)

    return control


def get_output_format_choices(parent, label):
    label = wx.StaticText(parent, label=label)
    control = wx.ComboBox(parent, style=wx.CB_SIMPLE|wx.CB_READONLY)
    try:
        control.SetSizerProps(expand=True)
    except AttributeError:
        pass

    for format in conversion.OutputFormat:
        control.Append(format.value, format.name)

    try:
        default_value = conversion.OutputFormat[application.config['default_output_format']].value
    except KeyError:
        default_value = conversion.OutputFormat['epub'].value

    control.SetStringSelection(default_value)
    return control

