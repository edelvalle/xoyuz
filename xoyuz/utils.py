#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoyuz.utils
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2013 Medardo Rodríguez
# All rights reserved.
#
# Author: Eddy Ernesto del Valle Pino <eddy@merchise.org>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


from __future__ import (
    absolute_import as _py3_abs_imports,
    division as _py3_division,
    print_function as _py3_print,
    unicode_literals as _py3_unicode
)

import re
import posixpath
from shutil import move
from subprocess import call
from os.path import join, splitext, dirname
from hashlib import sha1
try:
    from urllib.parse import unquote
except ImportError:     # Python 2
    from urllib import unquote

from xoutil.decorator import memoized_property
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.storage import default_storage


url_pattern = re.compile(r'url\(["\']?[^"\'\)]*[\'"]?\)')
url_extractor = re.compile(r'url\(["\']?(?P<url>[^"\'\)]*)[\'"]?\)')


class Bundle(object):
    def __init__(self, paths):
        self.paths = paths

    @memoized_property
    def concat_file_name(self):
        joined_paths = ''.join(self.paths)
        _, ext = splitext(joined_paths)
        return sha1(joined_paths).hexdigest() + ext

    @memoized_property
    def minified_file_name(self):
        return '%s.min%s' % splitext(self.concat_file_name)

    @memoized_property
    def concat_file_path(self):
        return join('resources', self.concat_file_name)

    @memoized_property
    def minified_file_path(self):
        return join('resources', self.minified_file_name)

    @property
    def minified_url(self):
        if not default_storage.exists(self.minified_file_path):
            self.concat_assets()
            self.minify()
        return default_storage.url(self.minified_file_path)

    def concat_assets(self):
        concat_file_content = FileContent(self.concat_file_path)
        for path in self.paths:
            normalized_path = posixpath.normpath(unquote(path)).lstrip('/')
            fs_path = finders.find(normalized_path)
            concat_file_content.append(open(fs_path).read(), path)

        real_path = default_storage.save(
            self.concat_file_path,
            concat_file_content
        )
        if real_path != self.concat_file_path:
            move(
                default_storage.path(real_path),
                default_storage.path(self.concat_file_path)
            )

    def minify(self):
        minified_file = default_storage.path(self.minified_file_path)
        concat_file = default_storage.path(self.concat_file_path)
        call(['yui-compressor', '-o', minified_file, concat_file])


class FileContent(object):
    def __init__(self, path):
        self._is_css = path.endswith('.css')
        self.content = []

    def append(self, chunk, path):
        if self._is_css:
            chunk = self.adjust_urls(chunk, path)
        self.content.append(chunk)

    def chunks(self):
        return self.content

    def adjust_urls(self, file_content, path):
        file_content = file_content.decode('utf8')
        replacements = {}
        for url_ref in url_pattern.findall(file_content):
            url = url_extractor.match(url_ref).groups()[0]
            replacements[url_ref] = 'url("../..%s%s/%s")' % (
                settings.STATIC_URL, dirname(path), url
            )
        for old, new in replacements.iteritems():
            file_content = file_content.replace(old, new)
        return file_content.encode('utf8')


def get_tags(urls):
    for url in urls:
        if url.endswith('js'):
            yield '<script src="%s"></script>' % url
        else:
            yield '<link href="%s" rel="stylesheet">' % url
