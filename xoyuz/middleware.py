#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xoyuz.middleware
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
from django.conf import settings
from django.template.response import SimpleTemplateResponse
from django.utils.html import strip_spaces_between_tags
from django.utils.encoding import force_text


def strip_tags(value):
    value = strip_spaces_between_tags(value)
    # compact all white spaces, except r'\n'
    value = re.sub(r'[ \t\r\f\v]+', ' ', force_text(value))
    return value


class SpacelessMidleware(object):
    """Remove the space between tags in `text/html` responses."""

    def process_response(self, request, response):
        if not settings.DEBUG and isinstance(response, SimpleTemplateResponse):
                response.content = strip_tags(
                    response.render().content
                )
        return response
