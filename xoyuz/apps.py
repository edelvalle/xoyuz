#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xoyuz.apps
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

from xoutil import fs

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from IPython.utils.importstring import import_item


class XoyuzConfig(AppConfig):
    name = 'xoyuz'
    verbose_name = _('Xoyuz static resources compressor')
    bundles = {}

    @property
    def bundles(self):
        self._bundles = getattr(self, '_bundles', {})
        return self._bundles

    @property
    def static_dir(self):
        static_dirs = [
            static_dir
            for static_dir in settings.STATICFILES_DIRS
            if isinstance(static_dir, (tuple, list))
        ]
        for prefix, static_dir in static_dirs:
            if prefix == 'xoyuz':
                return static_dir
        msg = (
            "Xoyuz can't find the static directory to compile the static "
            "resources. You must provide a configuration like:\n\n"
            "STATICFILES_DIRS = (\n"
            "    ('xoyuz', os.path.join(BASE_DIR, 'xoyuz')),\n"
            ")"
        )
        raise ImproperlyConfigured(msg)

    @property
    def js_compiler(self):
        return import_item(
            getattr(settings, 'XOYUZ_JS_COMPILER', 'xoyuz.compilers.closure')
        )

    @property
    def css_compiler(self):
        return import_item(
            getattr(settings, 'XOYUZ_CSS_COMPILER', 'xoyuz.compilers.yui')
        )

    def register_bundle(self, name, *args, **kwargs):
        from .bundle import Bundle
        if name in self.bundles:
            msg = 'Attempt to register two or more bundles with name "%s".'
            raise ImproperlyConfigured(msg % name)
        self.bundles[name] = Bundle(name, *args, **kwargs)

    def compile_bundles(self):
        fs.makedirs(self.static_dir, exist_ok=True)
        for bundle in self.bundles.values():
            bundle.compile()
