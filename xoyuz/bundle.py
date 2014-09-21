#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xoyuz.bundle
# --------------------------------------------------------------------------
# Copyright (c) 2014 Merchise Autrement and Contributors
# All rights reserved.
#
# Author: Eddy Ernesto del Valle Pino <eddy@merchise.org>
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.


from __future__ import (absolute_import as _py3_abs_imports,
                        division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import re
import posixpath
from urlparse import urljoin
from os.path import join, splitext, dirname
from hashlib import sha1
try:
    from urllib.parse import unquote
except ImportError:     # Python 2
    from urllib import unquote

from xoutil.decorator import memoized_property

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


class Bundle(object):

    JS_EXTENSION = '.js'
    CSS_EXTENSION = '.css'

    def __init__(self, name, files=(), require=()):
        if not files and not require:
            msg = 'Empty bundle "%s", does not has files or required bundles.'
            raise ImproperlyConfigured(msg % name)
        self.name = name
        self.files = files
        self.require_names = require

    @memoized_property
    def require(self):
        bundles = apps.get_app_config('xoyuz').bundles
        return [bundles[name] for name in self.require_names]

    @memoized_property
    def language(self):
        if self.files:
            name, ext = splitext(self.files[0])
            if ext == self.JS_EXTENSION:
                return 'javascript'
            elif ext == self.CSS_EXTENSION:
                return 'stylesheet'
            else:
                raise ValueError('Unknown file type: ' + self.files[0])

        return self.require[0].language

    @memoized_property
    def all_files(self):
        all_files = []
        for require in self.require:
            for file_name in require.all_files:
                if file_name not in all_files:
                    all_files.append(file_name)
        all_files.extend(self.files)
        return tuple(all_files)

    @memoized_property
    def all_urls(self):
        all_urls = []
        for require in self.require:
            all_urls.extend(require.all_urls)
        all_urls.extend(staticfiles_storage.url(url) for url in self.files)
        return tuple(all_urls)

    @property
    def ext(self):
        exts = {
            'javascript': self.JS_EXTENSION,
            'stylesheet': self.CSS_EXTENSION
        }
        return exts[self.language]

    @memoized_property
    def file_name(self):
        joined_paths = ''.join(self.all_files)
        return sha1(joined_paths).hexdigest() + self.ext

    @memoized_property
    def destination_path(self):
        return join(apps.get_app_config('xoyuz').static_dir, self.file_name)

    @memoized_property
    def file_path(self):
        return join('xoyuz', self.file_name)

    @memoized_property
    def url(self):
        return staticfiles_storage.url(self.file_path)

    def compile(self):
        print('Building %s -> %s...' % (self.name, self.file_path))
        compiled_file = CompiledFile(self.destination_path)
        for f_name in self.all_files:
            normalized_path = posixpath.normpath(unquote(f_name)).lstrip('/')
            fs_path = finders.find(normalized_path)
            if fs_path is None:
                raise ValueError('File not found "%s"' % normalized_path)
            else:
                content = open(fs_path).read()
            print('-', f_name)
            compiled_file.append(content, f_name)
        print()
        compiled_file.save()


class CompiledFile(object):

    url_pattern = re.compile(r'url\(["\']?[^"\'\)]*[\'"]?\)')
    url_extractor = re.compile(r'url\(["\']?(?P<url>[^"\'\)]*)[\'"]?\)')

    def __init__(self, path):
        self.path = path
        _, self.ext = splitext(path)
        self._is_css = self.ext == Bundle.CSS_EXTENSION
        self._is_minified = False
        self.content = []

    def append(self, chunk, path):
        """Append static resources to this file."""
        if self._is_css:
            chunk = self.adjust_urls(chunk, path)
        self.content.append(chunk.decode('utf8'))

    @property
    def compiler(self):
        config = apps.get_app_config('xoyuz')
        if self._is_css:
            return config.css_compiler
        else:
            return config.js_compiler

    def minify(self):
        if not self._is_minified:
            all_content = ''.join(self.content)
            self.content = self.compiler(all_content, self.ext).encode('utf8')
        self._is_minified = True

    def save(self):
        self.minify()
        with open(self.path, 'wb') as destination:
            destination.write(self.content)

    def adjust_urls(self, file_content, path):
        """Translate the URLs in a CSS file to absolute URLs."""
        file_content = file_content.decode('utf8')
        replacements = {}
        for url_ref in self.url_pattern.findall(file_content):
            url = self.url_extractor.match(url_ref).groups()[0]
            path_dirname = dirname(path)
            if path_dirname:
                path_dirname += '/'
            url = urljoin(settings.STATIC_URL, path_dirname + url)
            replacements[url_ref] = 'url("%s")' % url
        for old, new in replacements.iteritems():
            file_content = file_content.replace(old, new)
        return file_content.encode('utf8')
