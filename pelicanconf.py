#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Colm Ryan'
SITENAME = u'Tomorrow Said Toad'
SITETITLE = u'Tomorrow Said Toad'
SITESUBTITLE = 'Today I will take life easy...'
SITEURL = ''

THEME = "/home/cryan/repos/pelican-themes/Flex"
# MAIN_MENU = True

PATH = 'content'

TIMEZONE = 'US/Eastern'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),)

# Social widget
SOCIAL = (('github', 'http://github.com/caryan'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}

COPYRIGHT_YEAR = 2019
CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}
