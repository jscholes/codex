# Codex
# Copyright (C) 2020 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import os.path
import subprocess
import webbrowser

import wx
import wx.lib.sized_controls as sc

import application
import calibre
import clipboard
import conversion
import models
import paths

from . import conversion_pipeline
from . import dialogs
from .utils import create_button, create_labelled_field, get_output_format_choices


EMPTY_LIST_MESSAGE = -1


class MainWindow(sc.SizedFrame):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(None, -1, _(application.title), size=(800, 600), style=wx.DEFAULT_FRAME_STYLE, *args, **kwargs)
        self.Centre()
        self.setup_layout()
        self.create_menus()

    def open_readme(self):
        if not application.is_frozen:
            return
        documentation_directory = os.path.join(application.application_path, 'documentation')
        language = application.config['interface_language']
        readme_path = os.path.join(documentation_directory, 'readme-{0}.html'.format(language))
        if not os.path.exists(readme_path):
            readme_path = os.path.join(documentation_directory, 'readme-en.html')

        webbrowser.open(readme_path)

    def add_conversion(self, path):
        self.files_list.Append(path)
        if self.conversions_list.GetItemCount() > 0 and self.conversions_list.GetItemData(0) == EMPTY_LIST_MESSAGE:
            self.conversions_list.DeleteAllItems()
        self.conversions_list.Append([path])
        self.conversions_list.Focus(0)
        # self.conversions_list.Select(0)

    def remove_file(self, selected_item):
        if selected_item != -1:
            book = conversion.conversion_queue[selected_item]
            conversion.conversion_queue.remove(book)
            self.files_list.Delete(selected_item)
            self.conversions_list.DeleteItem(selected_item)
            try:
                if self.files_list.GetCount() != 0:
                    if selected_item == self.files_list.GetCount():
                        next_item_index = selected_item - 1
                    elif selected_item == 0:
                        next_item_index = 0
                    else:
                        next_item_index = selected_item
                    self.files_list.SetSelection(next_item_index)
                    self.conversions_list.Focus(next_item_index)
                    self.conversions_list.Select(next_item_index)
                else:
                    self.reset()
            except wx.PyAssertionError:
                pass

    def paste_files_from_clipboard(self):
        try:
            clipboard_paths = clipboard.get_files_from_clipboard()
            conversion_pipeline.add_paths(clipboard_paths, parent=self)
        except clipboard.NoFilesOnClipboardError:
            pass

    def setup_layout(self):
        main_panel = self.GetContentsPane()
        main_panel.SetSizerType('vertical')

        files_list_label = wx.StaticText(main_panel, label=_('Files'))
        self.files_list = wx.ListBox(main_panel, style=wx.LB_NEEDED_SB)
        self.files_list.SetSizerProps(expand=True, proportion=1)
        self.files_list.Bind(wx.EVT_CHAR, self.onFilesListKeyPressed)

        conversions_list_label = wx.StaticText(main_panel, label=_('&Conversions'))
        self.conversions_list = wx.ListCtrl(main_panel, style=wx.LC_REPORT)
        self.conversions_list.SetSizerProps(expand=True, proportion=1)
        self.conversions_list.Bind(wx.EVT_CHAR, self.onFilesListKeyPressed)
        self.conversions_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onFilesListSelectionChange)
        self.conversions_list.AppendColumn('Name')
        self.conversions_list.Append(['No files added for conversion.  Use the "Add" button or paste from your clipboard.'])

        files_list_buttons_panel = sc.SizedPanel(main_panel)
        files_list_buttons_panel.SetSizerType('horizontal')

        self.add_button = create_button(files_list_buttons_panel, _('&Add'), self.onAdd)
        self.remove_file_button = create_button(files_list_buttons_panel, _('&Remove file'), self.onRemoveFile)
        self.remove_file_button.Disable()

        self.main_buttons_panel = sc.SizedPanel(main_panel)
        self.main_buttons_panel.SetSizerType('horizontal')
        self.main_buttons_panel.Disable()

        self.output_formats = get_output_format_choices(self.main_buttons_panel, _('O&utput format'))
        self.output_formats.Disable()

        self.convert_button = create_button(self.main_buttons_panel, _('&Convert'), self.onConvert, wx.ID_CONVERT)
        self.convert_button.Disable()
        self.remove_drm_button = create_button(self.main_buttons_panel, _('Remove &DRM'), self.onRemoveDRM, wx.ID_CONVERT)
        self.remove_drm_button.Disable()

        self.conversions_list.SetItemData(0, EMPTY_LIST_MESSAGE)
        self.conversions_list.Focus(0)
        self.conversions_list.Select(0)

    def create_menus(self):
        file_menu = self.create_file_menu()
        tools_menu = self.create_tools_menu()
        help_menu = self.create_help_menu()
        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, _('&File'))
        menu_bar.Append(tools_menu, _('&Tools'))
        menu_bar.Append(help_menu, _('&Help'))
        self.SetMenuBar(menu_bar)
        self.add_menu = wx.Menu()
        add_files = self.add_menu.Append(wx.ID_OPEN, _('Add f&iles...\tCtrl+O'))
        self.Bind(wx.EVT_MENU, self.onAddFiles, add_files)
        add_directory = self.add_menu.Append(wx.NewId(), _('Add &directory...\tCtrl+D'))
        self.Bind(wx.EVT_MENU, self.onAddDirectory, add_directory)

    def create_file_menu(self):
        file_menu = wx.Menu()
        add_files = file_menu.Append(wx.ID_OPEN, _('Add f&iles...\tCtrl+O'))
        self.Bind(wx.EVT_MENU, self.onAddFiles, add_files)
        add_directory = file_menu.Append(wx.NewId(), _('Add &directory...\tCtrl+D'))
        self.Bind(wx.EVT_MENU, self.onAddDirectory, add_directory)
        file_menu.AppendSeparator()
        options = file_menu.Append(wx.ID_PREFERENCES, _('&Options...\tCtrl+P'))
        self.Bind(wx.EVT_MENU, self.onOptions, options)
        exit = file_menu.Append(wx.ID_EXIT, _('&Exit\tAlt+F4'))
        self.Bind(wx.EVT_MENU, self.onExit, exit)
        return file_menu

    def create_tools_menu(self):
        tools_menu = wx.Menu()
        find_book_from_url = tools_menu.Append(wx.NewId(), _('&Find Kindle file from Amazon URL...'))
        self.Bind(wx.EVT_MENU, self.onFindBookFromUrl, find_book_from_url)
        browse_kindle_books = tools_menu.Append(wx.NewId(), _('&Browse downloaded Kindle books...'))
        self.Bind(wx.EVT_MENU, self.onBrowseKindleBooks, browse_kindle_books)
        if not application.is_frozen:
            calibre_environment = tools_menu.Append(wx.NewId(), _('&Launch Calibre environment'))
            self.Bind(wx.EVT_MENU, self.onCalibreEnvironment, calibre_environment)
        return tools_menu

    def create_help_menu(self):
        help_menu = wx.Menu()
        help_menu_documentation = help_menu.Append(wx.NewId(), _('&Documentation'))
        self.Bind(wx.EVT_MENU, self.onDocumentation, help_menu_documentation)
        help_menu_home_page = help_menu.Append(wx.NewId(), _('&Codex home page'))
        self.Bind(wx.EVT_MENU, self.onHomePage, help_menu_home_page)
        help_menu_open_config_directory = help_menu.Append(wx.NewId(), _('&Open Codex configuration directory'))
        self.Bind(wx.EVT_MENU, self.onOpenConfigDirectory, help_menu_open_config_directory)
        help_menu_about = help_menu.Append(wx.ID_ABOUT, _('&About...'))
        self.Bind(wx.EVT_MENU, self.onAbout, help_menu_about)
        return help_menu

    def reset(self):
        self.remove_file_button.Disable()
        self.convert_button.Disable()
        self.remove_drm_button.Disable()
        self.main_buttons_panel.Disable()
        self.output_formats.Disable()
        self.files_list.Clear()
        self.conversions_list.SetFocus()

    def onFilesListKeyPressed(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE and self.files_list.GetCount() != 0:
            self.remove_file(self.files_list.GetSelection())
        elif event.GetKeyCode() == wx.WXK_CONTROL_V:
            self.paste_files_from_clipboard()
        else:
            event.Skip()

    def onFilesListSelectionChange(self, event):
        if event.GetIndex() >= 0 and self.conversions_list.GetItemData(0) != EMPTY_LIST_MESSAGE:
            self.remove_file_button.Enable()
        else:
            event.Skip()

    def onAdd(self, event):
        self.PopupMenu(self.add_menu, self.add_button.GetScreenPosition())

    def onAddFiles(self, event):
        file_dialog = wx.FileDialog(self, message=_('Please select the file(s) to be added'), defaultDir=application.config['working_directory'], wildcard=_('All supported files|{0}|All files|{1}').format(conversion.input_wildcards, '*.*'), style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        result = file_dialog.ShowModal()

        if result == wx.ID_OK:
            selected_paths = file_dialog.GetPaths()
            conversion_pipeline.add_paths(selected_paths, parent=self)
            application.config['working_directory'] = os.path.split(file_dialog.GetPath())[0]
            self.conversions_list.SetFocus()
            if self.files_list.GetCount() != 0:
                self.convert_button.Enable()
                self.remove_drm_button.Enable()
                self.main_buttons_panel.Enable()
                self.output_formats.Enable()

    def onAddDirectory(self, event):
        folder_dialog = wx.DirDialog(self, message=_('Please select the directory to be added'), defaultPath=application.config['working_directory'], style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        result = folder_dialog.ShowModal()

        if result == wx.ID_OK:
            conversion_pipeline.add_paths(paths.walk_directory_tree(folder_dialog.GetPath()), parent=self, from_folder=True)
            application.config['working_directory'] = os.path.split(folder_dialog.GetPath())[0]
            self.conversions_list.SetFocus()

    def onRemoveFile(self, event):
        if self.files_list.GetCount() != 0:
            self.remove_file(self.files_list.GetSelection())
            self.conversions_list.SetFocus()

    def onRemoveDRM(self, event):
        conversion.remove_drm_only = True
        conversion_pipeline.start(parent=self)
        self.reset()

    def onConvert(self, event):
        conversion.output_format = self.output_formats.GetClientData(self.output_formats.GetSelection())
        conversion_pipeline.start(parent=self)
        self.reset()

    def onOptions(self, event):
        options_dialog = dialogs.OptionsDialog(self)
        options_dialog.ShowModal()

    def onCalibreEnvironment(self, event):
        calibre.setup()
        subprocess.Popen(['cmd.exe'], cwd=calibre.calibre_path, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def onFindBookFromUrl(self, event):
        find_dialog = dialogs.FindBookFromURLDialog(self)
        find_dialog.ShowModal()

    def onBrowseKindleBooks(self, event):
        if not os.path.exists(application.config['kindle_content_directory']):
            wx.MessageBox(_('The configured Kindle content directory does not exist.'), _('Error'), wx.ICON_ERROR, parent=self)
            return

        kindle_files = os.listdir(application.config['kindle_content_directory'])
        kindle_files.sort(key=lambda path: os.stat(os.path.join(application.config['kindle_content_directory'], path)).st_ctime)
        kindle_files = [file for file in kindle_files if file.endswith('azw')]
        if len(kindle_files) == 0:
            wx.MessageBox(_('No Kindle files found.  Please make sure that the Kindle content directory setting is correct in the Codex Options dialog.'), _('Error'), wx.ICON_ERROR, parent=self)
            return

        books_dialog = dialogs.BrowseKindleBooksDialog(self, kindle_files)
        books_dialog.ShowModal()

    def onDocumentation(self, event):
        self.open_readme()

    def onHomePage(self, event):
        webbrowser.open(application.url)

    def onOpenConfigDirectory(self, event):
        os.startfile(application.config_directory)

    def onAbout(self, event):
        about_dialog = dialogs.AboutDialog(self)
        about_dialog.ShowModal()

    def onExit(self, event):
        self.Close()

def setup():
    if not hasattr(application, 'command_line_args'):
        application.main_window = MainWindow()
        application.wx_app.SetTopWindow(application.main_window)
        application.main_window.Show()
    else:
        args = application.command_line_args
        if not os.path.exists(args.path):
            wx.MessageBox(_('The specified file or directory does not exist.'), _('Error'), wx.ICON_ERROR, parent=None)
            return
        if os.path.isdir(args.path):
            conversion_pipeline.add_paths(paths.walk_directory_tree(args.path), from_folder=True)
            if len(conversion.conversion_queue) == 0:
                wx.MessageBox(_('No supported files were found in the specified directory.'), _('Error'), wx.ICON_ERROR, parent=None)
                return
        else:
            conversion_pipeline.add_paths([args.path])

        if len(conversion.conversion_queue) == 0:
            return

        conversion.remove_drm_only = args.remove_drm_only
        if not conversion.remove_drm_only:
            conversion.output_format = conversion.OutputFormat[args.format].name
        conversion_pipeline.start()
        return