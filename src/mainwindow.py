# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import PySide
import signal
import os, pprint
import time

from datastore import data
from config  import NxConfig
from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MainWindow(QObject):
    """
    The main window control class contains the application main container
    window and container tab widget. It commands global actions, like tab
    switching, exit handling, saving and loading.
    """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, argv):
        super().__init__()
        # load ui to data.w_*
        loader = QtUiTools.QUiLoader()
        for name, fname in (
            ('w_main',                  'forms/mainwindow.ui'),
            ('w_project',               'forms/project.ui'),
            ('w_project_diag_help',     'forms/project_help.ui'),
            ('w_log',                   'forms/log.ui'),
            ('w_roadmap',               'forms/roadmap.ui'),
            ('w_project_diag_new',      'forms/project_diag_new.ui'),
            ('w_project_diag_edit',     'forms/project_diag_edit.ui'),
            ('w_log_diag_new',          'forms/log_new_entry.ui'),
            ('w_roadmap_diag_add',      'forms/roadmap_add.ui'),
            ('w_roadmap_diag_finalize', 'forms/roadmap_finalize_milestone.ui')):
            f = QFile(fname)
            f.open(QFile.ReadOnly)
            obj = data.__dict__[name] = loader.load(f)
            f.close()
            if name.find('diag') > 0:
                obj.setParent(data.w_main)
                obj.setWindowFlags(Qt.Dialog)
        loader.deleteLater()
        # position module widgets
        for cname, pname in (('w_project', 'tab_project'),
                             ('w_log',     'tab_log'),
                             ('w_roadmap', 'tab_roadmap')):
            grid = QGridLayout()
            grid.addWidget(data.__dict__[cname], 0, 0)
            grid.setContentsMargins(0, 0, 0, 0)
            data.w_main.__dict__[pname].setLayout(grid)
        # icon and window size
        data.w_main.setWindowIcon(QIcon('img/nelia-icon32.png'))
        data.w_main.setGeometry(100,70,1000,600)

        # initialize modules
        data.run['mainwindow'] = self
        data.run['config']     = NxConfig()
        data.run['project']    = NxProject()
        data.run['log']        = NxLog()
        data.run['roadmap']    = NxRoadmap()

        # Dissable all tabs except the project tab.
        # They show the data from the selected project, and are in undefined
        # before a selection is made.
        self.dissableTabs()

        # Connect signals and slots.
        data.w_main.tabnavi.currentChanged.connect(self.tabChanged)

        # Global shortcuts.
        close_shortcut = QShortcut(QKeySequence('Ctrl+w'), data.w_main)
        close_shortcut.activated.connect(data.w_main.close)
        switch_forward = QShortcut(QKeySequence('Ctrl+PgUp'), data.w_main)
        switch_forward.activated.connect(self.onTabForward)
        switch_backward = QShortcut(QKeySequence('Ctrl+PgDown'), data.w_main)
        switch_backward.activated.connect(self.onTabBackward)
        save = QShortcut(QKeySequence('Ctrl+s'), data.w_main)
        save.activated.connect(self.onSaveShortcutActivated)
        debug = QShortcut(QKeySequence('Ctrl+d'), data.w_main)
        debug.activated.connect(self.debug)

        # Intercept close event (see self.eventFilter).
        QObject.installEventFilter(data.w_main, self)
        signal.signal(signal.SIGTERM, self.onExit)

        self.applyConfig()
        data.run['project'].reset()

        data.w_main.show()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSaveShortcutActivated(self):
        if data.run['changed']:
            data.run['project'].onSaveClicked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def debug(self):

        home = os.path.expanduser('~')
        with open(os.path.join(home, '.cache', 'nelia.debug.py'), 'w') as f:
            f.write(pprint.pformat(data.__dict__))

    def updateConfig(self):

        """
            Update configuration details. This is mostly the column widths.
        """
        data.run['project'].saveLayout()
        data.run['log'].saveLayout()
        data.run['roadmap'].saveLayout()
        data.run['config'].config_data['project']['header_width'] = \
                data.run['project'].header_width
        data.run['config'].config_data['project']['sort_column'] = \
                data.run['project'].sort_column
        data.run['config'].config_data['project']['sort_order'] = \
                data.run['project'].sort_order.__repr__()
        data.run['config'].config_data['log']['header_width'] = \
                data.run['log'].header_width
        data.run['config'].config_data['log']['sort_column'] = \
                data.run['log'].sort_column
        data.run['config'].config_data['log']['sort_order'] = \
                data.run['log'].sort_order.__repr__()
        data.run['config'].config_data['roadmap']['header_width'] = \
                data.run['roadmap'].header_width
        data.run['config'].config_data['roadmap']['sort_column'] = \
                data.run['roadmap'].sort_column
        data.run['config'].config_data['roadmap']['sort_order'] = \
                data.run['roadmap'].sort_order.__repr__()

        x = data.run['config'].config_data['roadmap']
        x['show_feature'] = data.w_roadmap.check_feature.isChecked()
        x['show_issue'] = data.w_roadmap.check_issue.isChecked()
        x['show_open'] = data.w_roadmap.check_open.isChecked()
        x['show_closed'] = data.w_roadmap.check_closed.isChecked()
        x['show_low'] = data.w_roadmap.check_low.isChecked()
        x['show_medium'] = data.w_roadmap.check_medium.isChecked()
        x['show_high'] = data.w_roadmap.check_high.isChecked()
        x['show_core'] = data.w_roadmap.check_core.isChecked()
        x['show_auxiliary'] = data.w_roadmap.check_auxiliary.isChecked()
        x['show_security'] = data.w_roadmap.check_security.isChecked()
        x['show_corrective'] = data.w_roadmap.check_corrective.isChecked()
        x['show_architecture'] = data.w_roadmap.check_architecture.isChecked()
        x['show_refactor'] = data.w_roadmap.check_refactor.isChecked()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def applyConfig(self):

        if data.run['config'].no_config == True:
            return

        data.run['project'].header_width = \
            data.run['config'].config_data['project']['header_width']
        data.run['project'].sort_column = \
            data.run['config'].config_data['project']['sort_column']
        if data.run['config'].config_data['project']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                data.run['project'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif data.run['config'].config_data['project']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                data.run['project'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        data.run['log'].header_width = \
            data.run['config'].config_data['log']['header_width']
        data.run['log'].sort_column = \
            data.run['config'].config_data['log']['sort_column']
        if data.run['config'].config_data['log']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                data.run['log'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif data.run['config'].config_data['log']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                data.run['log'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        data.run['roadmap'].header_width = \
            data.run['config'].config_data['roadmap']['header_width']
        data.run['roadmap'].sort_column = \
            data.run['config'].config_data['roadmap']['sort_column']
        if data.run['config'].config_data['roadmap']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                data.run['roadmap'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif data.run['config'].config_data['roadmap']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                data.run['roadmap'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        data.run['project'].loadLayout()
        data.run['log'].loadLayout()
        data.run['roadmap'].loadLayout()

        x = data.run['config'].config_data['roadmap']

        if x['show_feature']:
            data.w_roadmap.check_feature.setChecked(True)
        else:
            data.w_roadmap.check_feature.setChecked(False)
        if x['show_issue']:
            data.w_roadmap.check_issue.setChecked(True)
        else:
            data.w_roadmap.check_issue.setChecked(False)
        if x['show_open']:
            data.w_roadmap.check_open.setChecked(True)
        else:
            data.w_roadmap.check_open.setChecked(False)
        if x['show_closed']:
            data.w_roadmap.check_closed.setChecked(True)
        else:
            data.w_roadmap.check_closed.setChecked(False)

        if x['show_low']:
            data.w_roadmap.check_low.setChecked(True)
        else:
            data.w_roadmap.check_low.setChecked(False)
        if x['show_medium']:
            data.w_roadmap.check_medium.setChecked(True)
        else:
            data.w_roadmap.check_medium.setChecked(False)
        if x['show_high']:
            data.w_roadmap.check_high.setChecked(True)
        else:
            data.w_roadmap.check_high.setChecked(False)

        if x['show_core']:
            data.w_roadmap.check_core.setChecked(True)
        else:
            data.w_roadmap.check_core.setChecked(False)
        if x['show_auxiliary']:
            data.w_roadmap.check_auxiliary.setChecked(True)
        else:
            data.w_roadmap.check_auxiliary.setChecked(False)
        if x['show_security']:
            data.w_roadmap.check_security.setChecked(True)
        else:
            data.w_roadmap.check_security.setChecked(False)
        if x['show_corrective']:
            data.w_roadmap.check_corrective.setChecked(True)
        else:
            data.w_roadmap.check_corrective.setChecked(False)
        if x['show_architecture']:
            data.w_roadmap.check_architecture.setChecked(True)
        else:
            data.w_roadmap.check_architecture.setChecked(False)
        if x['show_refactor']:
            data.w_roadmap.check_refactor.setChecked(True)
        else:
            data.w_roadmap.check_refactor.setChecked(False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onExit(self, num, frame):
        """
        We want to shut down normally on SIGTERM too. This can happen when the
        computer is turned off, without closing the application first. This
        will issue the main window to close, which will trigger the event
        filter and shout down properly.
        """

        data.w_main.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def eventFilter(self, obj, event):
        """
        Capture main window close event.  This might be caused by the user
        clicking the (x) window button or by exiting via the Ctrl-w shortcut
        (or any other way that tells the main window to close).
        """

        if obj == data.w_main and isinstance(event, QCloseEvent):
            self.updateConfig()
            data.run['config'].writeConfig()
            # note: this does not actually work -> has to be debugged
            if data.run['changed']:
                if data.run['path']:
                    data.save_document(data.run['path'])
                else:
                    base = data.default_path
                    path = os.path.join(
                        base,'.'+str(int(time.time()))+'.tmp.nelia1')
                    data.save_document(path)
        res = False
        try:
            res = QObject.eventFilter(data.w_main, obj, event)
        except:
            pass
        return res

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabForward(self):

        # get current tab index
        tab_index = data.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = data.w_main.tabnavi.count()

        # next tab
        if tab_index+1 == tab_count:
            data.w_main.tabnavi.setCurrentIndex(0)
        elif data.w_main.tabnavi.isTabEnabled(tab_index+1):
            data.w_main.tabnavi.setCurrentIndex(tab_index+1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabBackward(self):

        # get current tab index
        tab_index = data.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = data.w_main.tabnavi.count()

        if tab_index == 0:
            if data.w_main.tabnavi.isTabEnabled(tab_count-1):
                data.w_main.tabnavi.setCurrentIndex(tab_count-1)
        else:
            data.w_main.tabnavi.setCurrentIndex(tab_index-1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def enableTabs(self):

        for i in range(1,3):
            data.w_main.tabnavi.setTabEnabled(i, True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dissableTabs(self):

        for i in range(1,3):
            data.w_main.tabnavi.setTabEnabled(i, False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tabChanged(self):

        # PREPARE DATA
        tab_widget = data.w_main.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == '&Log':
            data.run['log'].onShowTab()
        if cur_tab_name == '&Roadmap':
            data.run['roadmap'].onShowTab()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

