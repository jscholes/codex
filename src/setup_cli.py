import glob
import os
import os.path
import shutil
import string
import subprocess
import sys

from setuptools import setup, find_packages
import py2exe

import application

def get_locale_data_files():
    locale_data_files = []
    for match in glob.iglob('locale\\*\\LC_MESSAGES'):
        locale_data_files.append((match, glob.glob('{}\\*.mo'.format(match))))

    return locale_data_files

source_directory = os.path.abspath(os.path.dirname(__file__))
project_directory = os.path.abspath(os.path.join(source_directory, os.pardir))
distribution_directory = os.path.join(project_directory, '{0}-{1}'.format(application.title, application.version))
installer_template = os.path.join(project_directory, 'setup.iss.tpl')
installer_script = os.path.join(project_directory, 'setup.iss')
inno_setup_compile_command = [r'C:\Program Files (x86)\Inno Setup 5\ISCC.exe', installer_script]
calibre_source = os.path.join(project_directory, 'calibre')
calibre_destination = os.path.join(os.path.abspath(distribution_directory), 'calibre')

try:
    print('Removing previous distribution')
    shutil.rmtree(distribution_directory)
except FileNotFoundError:
    print('No previous distribution found')

setup(
    name=application.title,
    version=application.version,
    packages=find_packages(),
    console=['codex.pyw'],
    data_files=[
        ('calibre_base', ['calibre_base\\DeDRM_plugin.zip']),
        ('calibre_base\\calibre_config\\metadata_sources', ['calibre_base\\calibre_config\\metadata_sources\\ISBNDB.json']),
        ('calibre_base\\calibre_library', ['calibre_base\\calibre_library\\metadata.db']),
    ] + get_locale_data_files(),
    zipfile=None,
    options={
        'py2exe': {
            'optimize': 2,
            'dist_dir': distribution_directory,
        },
    },
)

print('Copying calibre files')
shutil.copytree(calibre_source, calibre_destination)
print('Removing build directory')
try:
    shutil.rmtree('build')
except WindowsError:
    print('Build directory not removed')

if '--no-installer' not in sys.argv:
    if os.path.exists(installer_script):
        print('Removing old installer script')
        os.remove(installer_script)

    print('Writing installer script file')
    with open(installer_template) as f:
        _installer_template = f.read()

    with open(installer_script, 'w') as f:
        f.write(string.Template(_installer_template).substitute(my_app_name=application.title, my_app_version=application.version, project_directory=project_directory, distribution_directory=distribution_directory))

    print('Building installer')
    subprocess.call(inno_setup_compile_command)