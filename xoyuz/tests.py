#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoyuz.tests
#----------------------------------------------------------------------
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

from xoutil.decorator import memoized_property

from django.test import TestCase
from django.core import management
from xoyuz import default_storage
from hashlib import sha1, md5

from .utils import get_tags, Bundle


class BundleTest(TestCase):
    PATHS = None
    LANGUAGE = None
    EXT = None
    MINIFICATION_MD5 = None

    def setUp(self):
        if self.PATHS:
            self.bundle = Bundle(self.PATHS)

    def tearDown(self):
        if self.PATHS:
            management.call_command('cleanminification')

    @memoized_property
    def paths_hash(self):
        if self.PATHS:
            return sha1(''.join(self.PATHS)).hexdigest()

    def test_language_detection(self):
        if self.PATHS:
            self.assertEqual(self.bundle.language, self.LANGUAGE)
            self.assertEqual(self.bundle.ext, self.EXT)

    def test_file_name(self):
        if self.PATHS:
            self.assertEqual(self.bundle.file_name, self.paths_hash + self.EXT)

    def test_file_path(self):
        if self.PATHS:
            self.assertEqual(
                self.bundle.file_path,
                'resources/%s%s' % (self.paths_hash, self.EXT)
            )

    def test_assets_compilation(self):
        if self.PATHS:
            self.bundle.compile_assets()
            self.assertTrue(default_storage.exists(self.bundle.file_path))
            content = default_storage.open(self.bundle.file_path).read()
            fhash = md5(content).hexdigest()
            self.assertEqual(fhash, self.MINIFICATION_MD5)
            self.assertEqual(
                self.bundle.url,
                '/media/resources/' + self.bundle.file_name
            )


class JavaScriptBundleTest(BundleTest):
    PATHS = ['xoyuz/test.js', 'xoyuz/test2.js']
    LANGUAGE = 'javascript'
    EXT = '.js'
    MINIFICATION_MD5 = 'a5fd2cc1c17c96b55e8251d4d63d7d90'


class StylesheetBundleTest(BundleTest):
    PATHS = ['xoyuz/test.css', 'xoyuz/test2.css']
    LANGUAGE = 'stylesheet'
    EXT = '.css'
    MINIFICATION_MD5 = '0f5cbde7a69243cfa54412aefec8cafe'


class FunctionsTest(TestCase):
    def test_get_tags(self):
        html = get_tags(['some/javascript.js', 'other.js', 'someother.css'])
        self.assertEqual(
            html,
            '<script src="some/javascript.js"></script>\n'
            '<script src="other.js"></script>\n'
            '<link href="someother.css" rel="stylesheet">'
        )
