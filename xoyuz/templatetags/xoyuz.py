#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoyuz.templatetags.xoyuz
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

from django import template
from django.conf import settings
from xoyuz.utils import Bundle, get_tags

register = template.Library()


@register.simple_tag
def resources(*urls):
    if settings.DEBUG:
        urls = [Bundle(urls).url]
    else:
        urls = [settings.STATIC_URL + url for url in urls]
    return '\n'.join(get_tags(urls))
