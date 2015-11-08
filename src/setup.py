# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import glob
import os
import os.path
import shutil
import string
import subprocess

import markdown
from setuptools import setup, find_packages
import py2exe

import application

source_directory = os.path.abspath(os.path.dirname(__file__))
project_directory = os.path.abspath(os.path.join(source_directory, os.pardir))
docs_directory = os.path.join(project_directory, 'docs')
distribution_directory = os.path.join(project_directory, '{0}-{1}'.format(application.title, application.version))
installer_template = os.path.join(project_directory, 'setup.iss.tpl')
installer_script = os.path.join(project_directory, 'setup.iss')
inno_setup_compile_command = [r'C:\Program Files (x86)\Inno Setup 5\ISCC.exe', installer_script]
calibre_source = os.path.join(project_directory, 'calibre')
calibre_destination = os.path.join(os.path.abspath(distribution_directory), 'calibre')

def get_locale_data_files():
    locale_data_files = []
    for match in glob.iglob('locale\\*\\LC_MESSAGES'):
        locale_data_files.append((match, glob.glob('{}\\*.mo'.format(match))))

    return locale_data_files

def generate_readme(language_code):
    default_tagline = 'Accessible eBook conversion and DRM removal'
    default_author_field = 'Author'
    default_version_field = 'Version'
    default_home_page_link_text = 'Project Home Page'

    readme_template = os.path.join(docs_directory, 'readme.tpl')
    source = os.path.join(docs_directory, language_code, 'readme.md')
    destination = os.path.join(distribution_directory, 'documentation')
    output_filename = os.path.join(destination, 'readme-{0}.html'.format(language_code))

    if not os.path.exists(source):
        raise FileNotFoundError(source)

    with open(source, 'r', encoding='utf-8') as f:
        text = f.read()

    converter = markdown.Markdown(extensions=['markdown.extensions.meta', 'markdown.extensions.toc'], output_format='html5')
    html = converter.convert(text)
    metadata = converter.Meta

    tagline = metadata.get('tagline', default_tagline)
    if isinstance(tagline, list):
        tagline = tagline[0]

    author_field = metadata.get('author_field', default_author_field)
    if isinstance(author_field, list):
        author_field = author_field[0]

    version_field = metadata.get('version_field', default_version_field)
    if isinstance(version_field, list):
        version_field = version_field[0]

    home_page_link_text = metadata.get('home_page_link_text', default_home_page_link_text)
    if isinstance(home_page_link_text, list):
        home_page_link_text = home_page_link_text[0]

    with open(readme_template, 'r', encoding='utf-8') as f:
        html_template = f.read()

    readme = string.Template(html_template)
    output = readme.safe_substitute(
        lang=language_code,
        title=application.title,
        version=application.version,
        tagline=tagline,
        author_field=author_field,
        author=application.author,
        version_field=version_field,
        url=application.url,
        home_page_link_text=home_page_link_text,
        content=html
    )

    try:
        os.makedirs(destination)
    except FileExistsError:
        pass

    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(output)

    return os.path.abspath(output_filename)

try:
    print('Removing previous distribution')
    shutil.rmtree(distribution_directory)
except FileNotFoundError:
    print('No previous distribution found')

setup(
    name=application.title,
    version=application.version,
    packages=find_packages(),
    windows=['codex.pyw'],
    data_files=[
        ('calibre_base', ['calibre_base\\DeDRM_plugin.zip']),
        ('calibre_base\\calibre_config\\metadata_sources', ['calibre_base\\calibre_config\\metadata_sources\\ISBNDB.json']),
        ('calibre_base\\calibre_library', ['calibre_base\\calibre_library\\metadata.db']),
        ('documentation', ['..\\docs\\style.css']),
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

print('Generating readme files')
working_directory = os.getcwd()
os.chdir(docs_directory)
for dir in os.listdir(docs_directory):
    if os.path.exists(os.path.join(dir, 'readme.md')):
        print('Generating readme for language {0}'.format(dir))
        readme = generate_readme(dir)
        print('Generated readme file {0}'.format(readme))

os.chdir(working_directory)

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
