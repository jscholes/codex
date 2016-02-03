# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.

import os.path
import re


class InvalidAmazonURLError(Exception):
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url


class BookNotFoundError(Exception):
    pass


AMAZON_URL_EXPRESSION = re.compile(r'^(https??://)??(www\.)??amazon\.([a-z\.]+)/(.*?)/dp/(?P<asin>B[a-zA-Z0-9]+?)(/.*?)??$')
EBOOK_SUFFIX = '_EBOK.azw'


def find_kindle_file_from_amazon_url(kindle_content_directory, url):
    asin = extract_asin_from_url(url)
    possible_path = construct_file_path_from_asin(kindle_content_directory, asin)
    if os.path.exists(possible_path):
        return possible_path
    else:
        raise BookNotFoundError


def extract_asin_from_url(url):
    url_match = AMAZON_URL_EXPRESSION.match(url)
    if not url_match:
        raise InvalidAmazonURLError(url)
    else:
        return url_match.group('asin')


def construct_file_path_from_asin(kindle_content_directory, asin):
    book_filename = '{0}{1}'.format(asin, EBOOK_SUFFIX)
    return os.path.join(kindle_content_directory, book_filename)