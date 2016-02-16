# Codex
# Copyright (C) 2015 James Scholes
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

class MainWindow(sc.SizedFrame):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(None, -1, _(application.title), size=(800, 600), style=wx.DEFAULT_FRAME_STYLE, *args, **kwargs)
        self.Centre()
        self.setup_layout()
        self.setup_tools_menu()
        self.setup_help_menu()

    def open_readme(self):
        if not application.is_frozen:
            return
        documentation_directory = os.path.join(application.application_path, 'documentation')
        language = application.config['interface_language']
        readme_path = os.path.join(documentation_directory, 'readme-{0}.html'.format(language))
        if not os.path.exists(readme_path):
            readme_path = os.path.join(documentation_directory, 'readme-en.html')

        webbrowser.open(readme_path)

    def remove_file(self, selected_item):
        if selected_item != -1:
            book = self.files_list.GetClientData(selected_item)
            conversion.conversion_queue.remove(book)
            self.files_list.Delete(selected_item)
            try:
                if self.files_list.GetCount() != 0:
                    if selected_item == self.files_list.GetCount():
                        next_item_index = selected_item - 1
                    elif selected_item == 0:
                        next_item_index = 0
                    else:
                        next_item_index = selected_item
                    self.files_list.SetSelection(next_item_index)
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

        files_list_label = wx.StaticText(main_panel, label=_('&Files'))
        self.files_list = wx.ListBox(main_panel, style=wx.LB_NEEDED_SB)
        self.files_list.SetSizerProps(expand=True, proportion=1)
        self.files_list.Bind(wx.EVT_CHAR, self.onFilesListKeyPressed)
        self.files_list.Bind(wx.EVT_LISTBOX, self.onFilesListSelectionChange)

        files_list_buttons_panel = sc.SizedPanel(main_panel)
        files_list_buttons_panel.SetSizerType('horizontal')

        add_files_button = create_button(files_list_buttons_panel, _('Add f&iles...'), self.onAddFiles)
        add_folder_button = create_button(files_list_buttons_panel, _('Add f&older...'), self.onAddFolder)
        self.remove_file_button = create_button(files_list_buttons_panel, _('&Remove file'), self.onRemoveFile)
        self.remove_file_button.Hide()

        main_buttons_panel = sc.SizedPanel(main_panel)
        main_buttons_panel.SetSizerType('horizontal')

        self.output_formats = get_output_format_choices(main_buttons_panel, _('Output &format'))

        convert_button = create_button(main_buttons_panel, _('&Convert'), self.onConvert, wx.ID_CONVERT)
        remove_drm_button = create_button(main_buttons_panel, _('Remove &DRM'), self.onRemoveDRM, wx.ID_CONVERT)
        options_button = create_button(main_buttons_panel, _('O&ptions'), self.onOptions, id=wx.ID_PREFERENCES)
        if not application.is_frozen:
            calibre_environment_button = create_button(main_buttons_panel, '&Launch Calibre environment', self.onCalibreEnvironment)
        self.tools_button = create_button(main_buttons_panel, _('&Tools'), self.onTools)
        self.help_button = create_button(main_buttons_panel, _('&Help'), self.onHelp, wx.ID_HELP)
        exit_button = create_button(main_buttons_panel, _('E&xit'), self.onExit, id=wx.ID_EXIT)

    def setup_tools_menu(self):
        self.tools_menu = wx.Menu()
        find_book_from_url = self.tools_menu.Append(wx.NewId(), _('&Find Kindle file from Amazon URL'))
        self.Bind(wx.EVT_MENU, self.onFindBookFromUrl, find_book_from_url)
        browse_kindle_books = self.tools_menu.Append(wx.NewId(), _('&Browse downloaded Kindle books'))
        self.Bind(wx.EVT_MENU, self.onBrowseKindleBooks, browse_kindle_books)

    def setup_help_menu(self):
        self.help_menu = wx.Menu()
        help_menu_documentation = self.help_menu.Append(wx.NewId(), _('&Documentation'))
        self.Bind(wx.EVT_MENU, self.onDocumentation, help_menu_documentation)
        help_menu_home_page = self.help_menu.Append(wx.NewId(), _('&Codex home page'))
        self.Bind(wx.EVT_MENU, self.onHomePage, help_menu_home_page)
        help_menu_open_config_directory = self.help_menu.Append(wx.NewId(), _('&Open Codex configuration directory'))
        self.Bind(wx.EVT_MENU, self.onOpenConfigDirectory, help_menu_open_config_directory)
        help_menu_about = self.help_menu.Append(wx.ID_ABOUT, _('&About'))
        self.Bind(wx.EVT_MENU, self.onAbout, help_menu_about)

    def reset(self):
        self.files_list.Clear()
        self.files_list.SetFocus()

    def onFilesListKeyPressed(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE and self.files_list.GetCount() != 0:
            self.remove_file(self.files_list.GetSelection())
        elif event.GetKeyCode() == wx.WXK_CONTROL_V:
            self.paste_files_from_clipboard()
        else:
            event.Skip()

    def onFilesListSelectionChange(self, event):
        if event.IsSelection():
            self.remove_file_button.Show()
        else:
            event.Skip()

    def onAddFiles(self, event):
        file_dialog = wx.FileDialog(self, message=_('Please select the file(s) to be added'), defaultDir=application.config['working_directory'], wildcard=_('All supported files|{0}|All files|{1}').format(conversion.input_wildcards, '*.*'), style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        result = file_dialog.ShowModal()

        if result == wx.ID_OK:
            selected_paths = file_dialog.GetPaths()
            conversion_pipeline.add_paths(selected_paths, parent=self)
            application.config['working_directory'] = os.path.split(file_dialog.GetPath())[0]
            application.config.write()
            self.files_list.SetFocus()

    def onAddFolder(self, event):
        folder_dialog = wx.DirDialog(self, message=_('Please select the folder to be added'), defaultPath=application.config['working_directory'], style=wx.DD_DEFAULT_STYLE|wx.DD_DIR_MUST_EXIST)
        result = folder_dialog.ShowModal()

        if result == wx.ID_OK:
            conversion_pipeline.add_paths(paths.walk_directory_tree(folder_dialog.GetPath()), parent=self, from_folder=True)
            application.config['working_directory'] = os.path.split(folder_dialog.GetPath())[0]
            application.config.write()
            self.files_list.SetFocus()

    def onRemoveFile(self, event):
        if self.files_list.GetCount() != 0:
            self.remove_file(self.files_list.GetSelection())
            self.files_list.SetFocus()

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

    def onTools(self, event):
        self.PopupMenu(self.tools_menu, self.help_button.GetScreenPosition())

    def onHelp(self, event):
        self.PopupMenu(self.help_menu, self.help_button.GetScreenPosition())

    def onFindBookFromUrl(self, event):
        find_dialog = dialogs.FindBookFromURLDialog(self)
        find_dialog.ShowModal()

    def onBrowseKindleBooks(self, event):
        if not os.path.exists(application.config['kindle_content_directory']):
            wx.MessageBox(_('The configured Kindle content directory does not exist.'), _('Error'), wx.ICON_ERROR, parent=self)
            return

        kindle_files = os.listdir(application.config['kindle_content_directory'])
        if len(kindle_files) == 0:
            wx.MessageBox(_('No Kindle files found.'), _('Error'), wx.ICON_ERROR, parent=self)
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