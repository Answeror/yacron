import logging
import os
import sys
import imp
import importlib
import re
from . import resources_rc
from PySide import QtGui, QtCore
from .const import VERSION
from fs.osfs import OSFS
from fs.watch import MODIFIED, CREATED


this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, this_dir)
import crython


log = logging.getLogger('yacron')


def init_log():
    logging.basicConfig(
        filename=os.path.join(os.path.expanduser('~'), 'yacron.log'),
        level=logging.DEBUG,
        format='%(asctime)s %(name)-16s %(levelname)-8s %(message)s'
    )
    soh = logging.StreamHandler(sys.stdout)
    soh.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(soh)


def md5(d):
    import hashlib
    m = hashlib.md5()
    m.update(d)
    return m.hexdigest()


def fmd5(path):
    with open(path, 'rb') as f:
        return md5(f.read())


class PluginManager(object):

    def load(self, root=None):
        if root is None:
            root = os.path.join(os.path.expanduser('~'), '.yacron')
        if not os.path.exists(root):
            import shutil
            plugin_dir = os.path.join(this_dir, '..', 'plugins')
            if not os.path.exists(plugin_dir):
                plugin_dir = os.path.join(os.path.dirname(sys.executable), 'plugins')
            if os.path.exists(plugin_dir):
                shutil.copytree(plugin_dir, root)
                f = QtCore.QFile(':/first.txt')
                if not f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                    assert False, f.errorString()
                QtGui.QMessageBox.information(None, 'first run', f.readAll().data().decode('utf-8'))
            else:
                log.error('default plugin directory %s not found' % plugin_dir)
                os.makedirs(root)

        sys.path.insert(0, root)

        mods = {}
        for filename in os.listdir(root):
            ret = re.search(r'^(yacron_(.+))\.py$', filename)
            if ret:
                name = ret.group(1)
                log.info('loading %s' % name)
                mods[name] = fmd5(os.path.join(root, filename)), importlib.import_module(name)

        self.fs = OSFS(root)

        @self.fs.add_watcher
        def reload(e):
            if type(e) in (MODIFIED, CREATED):
                filename = os.path.basename(e.path)
                ret = re.search(r'^(yacron_(.+))\.py$', filename)
                if ret:
                    name = ret.group(1)
                    signature = fmd5(os.path.join(root, filename))
                    if name in mods:
                        if mods[name][0] != signature:
                            log.info('reloading %s' % name)
                            mods[name] = signature, imp.reload(mods[name][1])
                    else:
                        log.info('loading %s' % name)
                        mods[name] = signature, importlib.import_module(name)


class Tray(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent):
        super(Tray, self).__init__(icon, parent)
        menu = QtGui.QMenu()
        menu.addAction('&About').triggered.connect(self.about)
        menu.addAction('&Exit').triggered.connect(QtGui.QApplication.instance().quit)
        self.setContextMenu(menu)

    def about(self):
        f = QtCore.QFile(':/about.txt')
        if not f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            assert False, f.errorString()
        QtGui.QMessageBox.about(
            self.parent(),
            self.tr('About'),
            self.tr(f.readAll().data().decode('utf-8') % VERSION)
        )


def main():
    init_log()
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName('helanic')
    app.setOrganizationDomain('answeror.com')
    app.setApplicationName('yacron')
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QtGui.QIcon(':/taskbar.png'))
    main = QtGui.QWidget()
    tray = Tray(QtGui.QIcon(':/tray.png'), main)
    tray.show()
    pm = PluginManager()
    if '-d' in sys.argv:
        pm.load(root='plugins')
    else:
        pm.load()
    crython.tab.start()
    sys.exit(app.exec_())
