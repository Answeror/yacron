#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
import os
from command import cmds
from functools import partial
import subprocess as sp


# see http://goo.gl/y6wgWV for details
version = sp.check_output(["git", "describe"]).decode('utf-8').strip()
with open('yacron/version.py.in', 'rb') as f:
    s = f.read().decode('ascii')
with open('yacron/version.py', 'wb') as f:
    f.write((s % version).encode('ascii'))

# cx-freeze 4.3.1 will ignore system bisect, don't know why
# include our own
includes = ['yacron.crython', 'yacron.bisect']
excludes = []
packages = ['http']
join = partial(os.path.join, 'plugins')
files = [(join(name), join(name)) for name in os.listdir('plugins') if name.endswith('.py')]

setup(
    name='yacron',
    version='0.1.0',
    packages=['yacron'],
    cmdclass=cmds,
    options={
        'build_exe': {
            'includes': includes,
            'excludes': excludes,
            'packages': packages,
            'include_files': files
        }
    },
    executables=[Executable(
        'run.py',
        base='Win32GUI',
        targetName='yacron.exe',
        compress=True,
        icon='yacron/images/smile.ico',
        shortcutName='yacron',
        shortcutDir='DesktopFolder'
    )]
)
