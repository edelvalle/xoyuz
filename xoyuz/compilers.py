#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# xoyuz.compilers
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

import os
from functools import wraps
from subprocess import check_output
from tempfile import mkstemp


def source_file_required(compiler):

    @wraps(compiler)
    def wrapper(source, ext):
        file_dsc, file_path = mkstemp(suffix=ext)
        with open(file_path, 'wb') as source_file:
            source_file.write(source.encode('utf-8'))
        result = compiler(file_path, ext)
        os.unlink(file_path)
        return result

    return wrapper


@source_file_required
def closure(source_file, ext):
    return check_output(
        [
            'closure-compiler',
            '--warning_level', 'QUIET',
            source_file,
        ]
    )


@source_file_required
def yui(source_file, ext):
    return check_output(['yui-compressor', source_file])


def css_min(source, ext):
    from cssmin import cssmin
    css = cssmin(source)
    # Revert `box-shadow`, webkit does not understands it.
    css = css.replace('box-shadow:0;', 'box-shadow:0 0;')
    return css


def js_min(source, ext):
    from jsmin import jsmin
    return jsmin(source)
