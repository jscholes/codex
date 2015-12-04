# -*- coding: utf-8 -*-
# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.
import builtins
import gettext
import os.path

import wx

import application

available_locales = {
    'en': ('English', wx.LANGUAGE_ENGLISH),
    'es': ('Español', wx.LANGUAGE_SPANISH),
}

def setup():
    application.logger.info('Available locales: {0}'.format(len(available_locales)))
    locale_path = os.path.join(application.application_path, 'locale')
    application.logger.info('Application locale path: {0}'.format(locale_path))

    locale_code = application.config.get('interface_language', 'en')
    try:
        locale_name, wx_locale = available_locales[locale_code]
    except KeyError as e:
        application.logger.error('No locale found for code: {0}'.format(e.message))
        locale_code = 'en'
        locale_name, wx_locale = available_locales[locale_code]

    trans = gettext.translation(domain=application.gettext_domain, localedir=locale_path, languages=[locale_code], fallback=True)
    trans.install()
    builtins.__dict__['__'] = trans.ngettext
    application.wx_app.locale = wx.Locale()
    application.wx_app.locale.AddCatalogLookupPathPrefix(locale_path)
    application.wx_app.locale.AddCatalog('wxstd')
    application.wx_app.locale.Init(language=wx_locale)

    application.logger.info('Application locale set to: {0} ({1})'.format(locale_name, locale_code))
