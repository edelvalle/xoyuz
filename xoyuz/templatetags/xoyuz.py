#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoyuz.templatetags.xoyuz
#----------------------------------------------------------------------
# Copyright (c) 2013-2014 Merchise Autrement and Contributors
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

from os.path import splitext

from django import template
from django.apps import apps
from django.conf import settings

register = template.Library()


@register.simple_tag
def resources(name):
    xoyuz = apps.get_app_config('xoyuz')
    bundle = xoyuz.bundles[name]
    if not settings.DEBUG:
        urls = [bundle.url]
    else:
        urls = bundle.all_urls
    return get_tags(urls)


def get_tags(urls):
    """Take static resource address and return the appropriate HTML tag."""
    tags = []
    for url in urls:
        name, ext = splitext(url)
        if ext == '.js':
            tag = '<script src="%s.js"></script>'
        else:
            tag = '<link href="%s.css" rel="stylesheet">'
        tags.append(tag % name)
    return '\n'.join(tags)
