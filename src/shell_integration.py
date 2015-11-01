# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import os.path
import sys
import winreg
from winreg import *

import application
import conversion

class ShellIntegrationError(Exception):
    pass

class ShellIntegrationNotSupportedError(Exception):
    pass

READ_PERMISSIONS = KEY_ENUMERATE_SUB_KEYS|KEY_QUERY_VALUE|KEY_READ|KEY_WOW64_64KEY
WRITE_PERMISSIONS = KEY_CREATE_SUB_KEY|KEY_SET_VALUE|KEY_WRITE|KEY_WOW64_64KEY
HIVE = 'HKEY_CURRENT_USER'
HIVE_HANDLE = getattr(winreg, HIVE)
REGISTRY_LOCATION = r'Software\Classes'
CLSID = 'AllFilesystemObjects'
SHELL_BRANCH = 'CodexShellIntegration'

if not application.is_frozen:
    entrypoint = '"{0}" "{1}"'.format(sys.executable, os.path.join(application.application_path, 'codex.pyw'))
else:
    entrypoint = '"{0}"'.format(os.path.join(application.application_path, 'codex.exe'))

root_menu = {
    'id': 'RootMenu',
    'label': 'Code&x',
    'commands': [
        {'id': 'Convert', 'label': _('&Convert'), 'command': '{0} "%1"'.format(entrypoint)},
        {'id': 'RemoveDRM', 'label': _('&Remove DRM'), 'command': '{0} -r "%1"'.format(entrypoint)},
        ],
}

convert_to_menu = {
    'id': 'ConvertToMenu',
    'parent': root_menu,
    'label': _('C&onvert to'),
    'commands': [{'id': format.name, 'label': format.value, 'command': '{0} -f {1} "%1"'.format(entrypoint, format.name)} for format in conversion.OutputFormat]
}

menu_tree = (root_menu, convert_to_menu)

def log(action, path, key=None, value=None):
    message = '{0}: {1}\\{2}'.format(action.capitalize(), HIVE, path)
    if key is not None and value is not None:
        message = '{0}: {1}={2}'.format(message, key, value)

    application.logger.debug(message)

def is_integrated():
    try:
        path = '{0}\\{1}\\shell\\{2}'.format(REGISTRY_LOCATION, CLSID, SHELL_BRANCH)
        log('open', path)
        codex = OpenKeyEx(HIVE_HANDLE, path, access=READ_PERMISSIONS)
        codex.Close()
        return True
    except (OSError, EnvironmentError, FileNotFoundError): # the documentation doesn't seem very clear (or correct) about which of these will be raised
        return False

def create_menu(menu):
    base = r'{location}\{clsid}\shell\{shell_branch}'.format(location=REGISTRY_LOCATION, clsid=CLSID, shell_branch=SHELL_BRANCH)
    commands_base = r'{base}\{menu_id}\shell'.format(base=base, menu_id=menu['id'])

    for command in menu['commands']:
        command_path = r'{base}\{command_id}'.format(base=commands_base, command_id=command['id'])
        log('create', command_path)
        command_handle = CreateKeyEx(HKEY_CURRENT_USER, command_path, access=WRITE_PERMISSIONS)
        key = 'MUIVerb'
        value = command['label']
        log('set', command_path, key, value)
        SetValueEx(command_handle, key, 0, REG_SZ, value)
        key = 'command'
        value = command['command']
        log('set', command_path, key, value)
        SetValue(command_handle, key, REG_SZ, value)
        command_handle.Close()

    if 'parent' in menu.keys():
        menu_descriptor = r'{base}\{parent_id}\shell\{menu_id}'.format(base=base, parent_id=menu['parent']['id'], menu_id=menu['id'])
    else:
        menu_descriptor = base

    log('create', menu_descriptor)
    descriptor_handle = CreateKeyEx(HKEY_CURRENT_USER, menu_descriptor, access=WRITE_PERMISSIONS)
    key = 'MUIVerb'
    value = menu['label']
    log('set', menu_descriptor, key, value)
    SetValueEx(descriptor_handle, key, 0, REG_SZ, value)
    key = 'ExtendedSubCommandsKey'
    value = r'{clsid}\shell\{shell_branch}\{menu_id}'.format(clsid=CLSID, shell_branch=SHELL_BRANCH, menu_id=menu['id'])
    log('set', menu_descriptor, key, value)
    SetValueEx(descriptor_handle, key, 0, REG_SZ, value)
    descriptor_handle.Close()

def integrate():
    windows_version = sys.getwindowsversion()
    windows_version = float('{0}.{1}'.format(windows_version.major, windows_version.minor))
    if windows_version < 6.1:
        raise ShellIntegrationNotSupportedError
        return

    for menu in menu_tree:
        create_menu(menu)

def setup():
    try:
        if not is_integrated() or hasattr(application, 'reset_shell_integration'):
            integrate()
            try:
                application.config.pop('shell_integration_not_supported')
                application.config.write()
            except KeyError:
                pass
        else:
            application.logger.debug('Shell integration already set up.')
    except PermissionError:
        raise ShellIntegrationError

    application.logger.debug('Command line entrypoint: {0}'.format(entrypoint))
