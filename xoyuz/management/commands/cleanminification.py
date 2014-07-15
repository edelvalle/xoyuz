#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoyuz.management.commands.collectstatic
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


from __future__ import (
    absolute_import as _py3_abs_imports,
    division as _py3_division,
    print_function as _py3_print,
    unicode_literals as _py3_unicode
)

from shutil import rmtree
from django.core.management.base import BaseCommand

from django.contrib.staticfiles.storage import staticfiles_storage


class Command(BaseCommand):
    help = 'Removes the minified files'

    def handle(self, *args, **kwargs):
        rmtree(staticfiles_storage.path('resources'), ignore_errors=True)
