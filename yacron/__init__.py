import crython
import logging
import os
import sys
import imp
import re
from . import resources_rc
from PySide import QtGui, QtCore
from .const import VERSION


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


def load_plugins(root=None):
    if root is None:
        root = os.path.join(os.path.expanduser('~'), '.yacron')
    if not os.path.exists(root):
        os.makedirs(root)
    for filename in os.listdir(root):
        ret = re.search(r'^yacron_(.+)\.py$', filename)
        if ret:
            name = ret.group(1)
            log.info('loading %s' % name)
            imp.load_source(name, os.path.join(root, filename))


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
    if '-d' in sys.argv:
        load_plugins(root='plugins')
    else:
        load_plugins()
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName('helanic')
    app.setOrganizationDomain('answeror.com')
    app.setApplicationName('yacron')
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QtGui.QIcon(':/taskbar.png'))
    main = QtGui.QWidget()
    tray = Tray(QtGui.QIcon(':/tray.png'), main)
    tray.show()
    crython.tab.start()
    sys.exit(app.exec_())
