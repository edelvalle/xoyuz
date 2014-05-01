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


from __future__ import (
    absolute_import as _py3_abs_imports,
    division as _py3_division,
    print_function as _py3_print,
    unicode_literals as _py3_unicode
)


from django.test import TestCase
from django.core import management
from django.core.files.storage import default_storage
from hashlib import sha1, md5

from .utils import get_tags, Bundle


class JavaScriptBundleTest(TestCase):
    PATHS = ['xoyuz/test.js', 'xoyuz/test2.js']
    PATHS_HASH = sha1(''.join(PATHS)).hexdigest()

    def setUp(self):
        self.bundle = Bundle(self.PATHS)

    def tearDown(self):
        management.call_command('cleanminification')

    def test_object_state(self):
        self.assertEqual(self.bundle.language, 'javascript')
        self.assertEqual(self.bundle.ext, '.js')

    def test_file_name(self):
        self.assertEqual(self.bundle.file_name, self.PATHS_HASH + '.js')

    def test_file_path(self):
        self.assertEqual(
            self.bundle.file_path,
            'resources/%s.js' % self.PATHS_HASH
        )

    def test_compile_assets(self):
        self.bundle.compile_assets()
        self.assertTrue(default_storage.exists(self.bundle.file_path))
        self.assertEqual(
            default_storage.size(self.bundle.file_path),
            110,
        )
        content = default_storage.open(self.bundle.file_path).read()
        fhash = md5(content).hexdigest()
        self.assertEqual(fhash, 'a5fd2cc1c17c96b55e8251d4d63d7d90')
        self.assertEqual(
            self.bundle.url,
            '/media/resources/' + self.bundle.file_name
        )


class StylesheetBundleTest(TestCase):
    pass


class FunctionsTest(TestCase):
    def test_get_tags(self):
        html = get_tags(['some/javascript.js', 'other.js', 'someother.css'])
        self.assertEqual(
            html,
            '<script src="some/javascript.js"></script>\n'
            '<script src="other.js"></script>\n'
            '<link href="someother.css" rel="stylesheet">'
        )
