#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
from command import cmds
import subprocess as sp


# see http://goo.gl/y6wgWV for details
version = sp.check_output(["git", "describe"]).decode('utf-8').strip()

includes = []
excludes = []
files = ['plugins/']

setup(
    name='yacron',
    version='0.1.0',
    packages=['yacron'],
    cmdclass=cmds,
    options={
        'build_exe': {
            'includes': includes,
            'excludes': excludes,
            'include_files': files
        }
    },
    executables=[Executable(
        'run.py',
        base='Win32GUI',
        targetName='yacron.exe',
        compress=True,
        icon='images/smile.ico'
    )]
)
