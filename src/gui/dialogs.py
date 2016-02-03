# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import os
import os.path
import sys
import time

import wx
from wx.lib import sized_controls as sc

import application
import calibre
import clipboard
import conversion
import kindle_finder
from signals import conversion_started, conversion_error, conversion_complete

import gui.conversion_pipeline
from .utils import create_button, create_labelled_field, get_output_format_choices

class BaseDialog(sc.SizedDialog):
    def __init__(self, parent, *args, **kwargs):
        super(BaseDialog, self).__init__(parent=parent, id=-1, title=self._title, style=wx.DEFAULT_DIALOG_STYLE, *args, **kwargs)
        self.Centre(wx.BOTH)
        self.panel = self.GetContentsPane()
        self.panel.SetSizerType('form')
        self.setup_layout()
        self.Fit()

    def setup_layout(self):
        raise NotImplementedError



class ConversionProgressDialog(BaseDialog):
    def __init__(self, parent, *args, **kwargs):
        if conversion.remove_drm_only:
            self._title = _('Removing DRM...')
        else:
            self._title = _('Converting...')
        self.counter = 1
        self.current_file = conversion.conversion_queue[0].input_path
        self.files_to_be_converted = len(conversion.conversion_queue)
        self.is_cancelled = False
        conversion.stop_conversion.clear()
        conversion_started.connect(self.onConversionStarted)
        conversion_error.connect(self.onConversionError)
        conversion_complete.connect(self.onConversionComplete)
        super(ConversionProgressDialog, self).__init__(parent=parent, *args, **kwargs)
        self.conversion_worker = conversion.ConversionWorker()
        self.conversion_worker.start()

    def setup_layout(self):
        self.progress_text = wx.StaticText(self.panel)
        self.current_file_text = wx.StaticText(self.panel)
        self.progress_bar = wx.Gauge(self.panel, -1, range=100, style=wx.GA_VERTICAL)
        self.progress_bar.SetSizerProps(expand=True)
        self.progress_bar.Pulse()
        self.update_progress()

        button_sizer = wx.StdDialogButtonSizer()
        if len(conversion.conversion_queue) > 1:
            self.skip_button = create_button(self.panel, _('&Skip'), self.onSkip)
            button_sizer.AddButton(self.skip_button)
        self.cancel_button = wx.Button(self.panel, wx.ID_CANCEL)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
        button_sizer.AddButton(self.cancel_button)
        self.SetButtonSizer(button_sizer)
        self.SetEscapeId(wx.ID_CANCEL)

    def update_progress(self):
        self.progress_bar.SetValue(self.calculate_progress())
        if conversion.remove_drm_only:
            verb = _('Removing DRM from')
        else:
            verb = _('Converting')
        self.progress_text.SetLabel(_('{0} file {1} of {2}').format(verb, self.counter, self.files_to_be_converted))
        self.current_file_text.SetLabel(self.current_file)

    def calculate_progress(self):
        # First, get the percentage increase for a single file to subtract it from the overall progress,
        # because otherwise we end up showing 25% when conversion has only just started
        single_file_percentage = int(round((1 / self.files_to_be_converted) * 100))
        if single_file_percentage < 0:
            single_file_percentage = 0

        progress = int(round(((self.counter / self.files_to_be_converted) * 100) - single_file_percentage))
        return progress

    def onConversionStarted(self, sender, **kwargs):
            self.counter = kwargs['count']
            self.current_file = kwargs['path']
            self.update_progress()

    def onConversionError(self, sender, **kwargs):
        wx.MessageBox(kwargs['error_msg'], _('Error'), wx.ICON_ERROR, parent=self)
        self.EndModal(wx.ID_CANCEL)

    def onConversionComplete(self, sender, **kwargs):
        self.progress_bar.SetValue(100)
        self.EndModal(wx.ID_CANCEL)

    def onCancel(self, event):
        if self.is_cancelled:
            return

        if hasattr(self, 'skip_button'):
            self.skip_button.Hide()
        self.cancel_button.SetLabel(_('Cancelling...'))
        self.is_cancelled = True
        conversion.stop_conversion.set()

    def onSkip(self, event):
        conversion.skip_current_file.set()



class ConversionCompleteDialog(BaseDialog):
    def __init__(self, parent, *args, **kwargs):
        if conversion.remove_drm_only:
            if len(conversion.converted_files) == 0:
                self._title = _('DRM not removed')
            else:
                self._title = _('DRM removed')
        else:
            self._title = _('Conversion Complete')
        super(ConversionCompleteDialog, self).__init__(parent=parent, *args, **kwargs)

    def copy_selected_books_to_clipboard(self):
        selected_items = self.converted_files.GetSelections()
        book_paths = []
        for index in selected_items:
            book_paths.append(self.converted_files.GetClientData(index).output_path.lstrip('\\\\?\\'))

        try:
            clipboard.put_files_on_clipboard(book_paths)
            books_copied = len(book_paths)
            application.speaker.speak(__('Copied {0} book to clipboard', 'Copied {0} books to clipboard', books_copied).format(books_copied))
        except clipboard.SetClipboardDataError:
            application.speaker.speak(_('Error copying books to clipboard'))

    def setup_layout(self):
        if len(conversion.converted_files) > 0:
            if conversion.remove_drm_only:
                converted_files_label = wx.StaticText(self.panel, label=_('&Processed files'))
            else:
                converted_files_label = wx.StaticText(self.panel, label=_('&Converted files'))
            self.converted_files = wx.ListBox(self.panel, style=wx.LB_NEEDED_SB|wx.LB_EXTENDED)
            self.converted_files.SetSizerProps(expand=True, proportion=1)
            self.converted_files.Bind(wx.EVT_CHAR, self.onConvertedFilesKeyPressed)

            for book in conversion.converted_files:
                book_string = '{0} - {1}'.format(book.author, book.title)
                self.converted_files.Append(book_string, book)

            self.converted_files.SetSelection(0)
            self.open_file_button = create_button(self.panel, _('&Open file'), self.onOpenFile)
            self.open_folder_button = create_button(self.panel, _('Open fol&der'), self.onOpenFolder)

        if len(conversion.failed_conversions) > 0:
            failed_conversions_label = wx.StaticText(self.panel, label=_('&Errors'))
            self.failed_conversions = wx.ListBox(self.panel, style=wx.LB_NEEDED_SB)
            self.failed_conversions.SetSizerProps(expand=True, proportion=1)
            self.failed_conversions.Set([book.input_path for book in conversion.failed_conversions])
            self.failed_conversions.SetSelection(0)

        close_button = wx.Button(self.panel, wx.ID_CLOSE)
        button_sizer = wx.StdDialogButtonSizer()
        button_sizer.AddButton(close_button)
        self.SetButtonSizer(button_sizer)
        self.SetEscapeId(wx.ID_CLOSE)

    def onConvertedFilesKeyPressed(self, event):
        if event.GetKeyCode() == wx.WXK_CONTROL_C:
            try:
                self.copy_selected_books_to_clipboard()
            except wx.PyAssertionError:
                pass
        else:
            event.Skip()

    def onOpenFile(self, event):
        try:
            book = self.converted_files.GetClientData(self.converted_files.GetSelections()[0])
            os.startfile(book.output_path)
            if len(conversion.converted_files) == 1 and len(conversion.failed_conversions) == 0:
                self.EndModal(wx.ID_CLOSE)
        except wx.PyAssertionError:
            wx.MessageBox(_('No file selected.'), _('Error'), wx.ICON_ERROR, parent=self)

    def onOpenFolder(self, event):
        try:
            book = self.converted_files.GetClientData(self.converted_files.GetSelections()[0])
            os.startfile(os.path.dirname(book.output_path))
        except wx.PyAssertionError:
            wx.MessageBox(_('No file selected.'), _('Error'), wx.ICON_ERROR, parent=self)



class OptionsDialog(BaseDialog):
    _title = _('Codex Options')

    def create_checkbox(self, parent, label, config_key):
        control = wx.CheckBox(parent, -1, label)
        control.SetValue(application.config[config_key])

        return control

    def setup_layout(self):
        self.output_options = wx.StaticBox(self.panel, -1, _('Output options'))
        self.conversion_options = wx.StaticBox(self.panel, -1, _('Conversion options'))

        self.output_directory = create_labelled_field(self.output_options, _('&Output directory'), application.config['output_directory'])
        output_directory_browse_button = create_button(self.output_options, _('&Browse...'), self.onOutputDirectoryBrowse)
        self.output_filename_template = create_labelled_field(self.output_options, _('&Output filename template'), application.config['filename_template'])
        self.default_output_format = get_output_format_choices(self.output_options, _('&Default output format'))

        self.show_conversion_complete_dialog = self.create_checkbox(self.conversion_options, _('&Show conversion complete dialog'), 'show_conversion_complete_dialog')
        self.remove_smart_punctuation = self.create_checkbox(self.conversion_options, _('&Remove smart punctuation from converted files'), 'remove_smart_punctuation')
        self.asciiize = self.create_checkbox(self.conversion_options, _('Re&place unicode characters with their ASCII equivalents (not recommended)'), 'asciiize')

        ok_button = wx.Button(self.panel, wx.ID_OK)
        cancel_button = wx.Button(self.panel, wx.ID_CANCEL)
        ok_button.Bind(wx.EVT_BUTTON, self.onOK)
        button_sizer = wx.StdDialogButtonSizer()
        button_sizer.AddButton(ok_button)
        button_sizer.AddButton(cancel_button)
        self.SetButtonSizer(button_sizer)
        self.SetAffirmativeId(wx.ID_OK)
        self.SetEscapeId(wx.ID_CANCEL)

    def onOutputDirectoryBrowse(self, event):
        folder_dialog = wx.DirDialog(self, message=_('Please select the new output directory'), defaultPath=application.working_path, style=wx.DD_DEFAULT_STYLE)
        result = folder_dialog.ShowModal()

        if result == wx.ID_OK:
            self.output_directory.SetValue(folder_dialog.GetPath())

    def onOK(self, event):
        should_save = False
        output_directory = os.path.expandvars(self.output_directory.GetValue())
        if os.path.exists(output_directory) and os.path.isdir(output_directory):
            should_save = True
        elif not os.path.exists(output_directory):
            should_create_folder = wx.MessageBox(_('The output directory you\'ve chosen doesn\'t exist.  Would you like to create it?'), _('Information'), wx.YES_NO|wx.ICON_QUESTION, parent=self)
            if should_create_folder == wx.YES:
                os.makedirs(output_directory)
                should_save = True
        elif not os.path.isdir(output_directory):
            wx.MessageBox(_('The output directory you\'ve chosen is not a folder!'), _('Error'), wx.ICON_ERROR, parent=self)

        if should_save:
            application.config['output_directory'] = output_directory
            application.config['filename_template'] = self.output_filename_template.GetValue()
            application.config['default_output_format'] = self.default_output_format.GetClientData(self.default_output_format.GetSelection())
            application.config['show_conversion_complete_dialog'] = self.show_conversion_complete_dialog.IsChecked()
            application.config['remove_smart_punctuation'] = self.remove_smart_punctuation.IsChecked()
            application.config['asciiize'] = self.asciiize.IsChecked()
            application.main_window.output_formats.SetStringSelection(self.default_output_format.GetStringSelection())

            validation_result = application.config.validate(application.config_validator)
            if validation_result == True:
                application.config.write()
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox(_('There was a problem saving your configuration.'), _('Error'), wx.ICON_ERROR, parent=self)
                application.logger.error('Config validation error: {0}'.format(validation_result))



class FindBookFromURLDialog(BaseDialog):
    _title = _('Find Kindle eBook File from Amazon URL')

    def setup_layout(self):
        dialog_label = wx.StaticText(self.panel)
        dialog_label.SetLabel(_('To easily locate the eBook file for a Kindle book you\'ve just purchased and downloaded to this computer, please enter the URL of the book\'s product page on Amazon.'))
        self.url = create_labelled_field(self.panel, _('&Amazon URL'))
        ok_button = wx.Button(self.panel, wx.ID_OK)
        cancel_button = wx.Button(self.panel, wx.ID_CANCEL)
        ok_button.Bind(wx.EVT_BUTTON, self.onOK)
        button_sizer = wx.StdDialogButtonSizer()
        button_sizer.AddButton(ok_button)
        button_sizer.AddButton(cancel_button)
        self.SetButtonSizer(button_sizer)
        self.SetAffirmativeId(wx.ID_OK)
        self.SetEscapeId(wx.ID_CANCEL)

    def onOK(self, event):
        try:
            ebook_path = kindle_finder.find_kindle_file_from_amazon_url(application.config['kindle_content_directory'], self.url.GetValue())
            gui.conversion_pipeline.add_paths([ebook_path], parent=self)
            self.EndModal(wx.ID_OK)
        except kindle_finder.InvalidAmazonURLError as e:
            wx.MessageBox(_('{0} doesn\'t seem to be a valid Amazon product URL.').format(e.url), _('Error'), wx.ICON_ERROR, parent=self)
        except kindle_finder.BookNotFoundError:
            wx.MessageBox(_('Codex was unable to locate an eBook file for this product on your computer.  If you\'ve changed the location of your Kindle content directory within the Kindle for PC software, please also change the corresponding setting in the Codex Options dialog.'), _('Error'), wx.ICON_ERROR, parent=self)


class AboutDialog(BaseDialog):
    _title = _('About {name}').format(name=application.title)

    def setup_layout(self):
        version = create_labelled_field(self.panel, _('&Version'), application.version, read_only=True)
        button_sizer = self.CreateButtonSizer(wx.CLOSE)
        self.SetButtonSizer(button_sizer)
        version.SetFocus()



