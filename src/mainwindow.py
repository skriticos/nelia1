# ------------------------------------------------------------------------------
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# All rights reserved
# ------------------------------------------------------------------------------
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import PySide
import signal
import os, pprint

from datastore import NxDataStore
from config  import NxConfig
from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap

# ------------------------------------------------------------------------------
class MainWindow(QObject):
    """
    The main window control class contains the application main container
    window and container tab widget. It commands global actions, like tab
    switching, exit handling, saving and loading.
    """

# ------------------------------------------------------------------------------
    def __init__(self, argv):

        super().__init__()

        # setup datastore
        data = self.data = NxDataStore(self)

        # Load UI
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
            obj = self.__dict__[name] = loader.load(f)
            f.close()
            if name.find('diag') > 0:
                obj.setParent(self.w_main)
                obj.setWindowFlags(Qt.Dialog)
            self.data.run[name] = obj
        loader.deleteLater()

        # position module widgets
        for cname, pname in (('w_project', 'tab_project'),
                             ('w_log',     'tab_log'),
                             ('w_roadmap', 'tab_roadmap')):
            grid = QGridLayout()
            grid.addWidget(self.__dict__[cname], 0, 0)
            grid.setContentsMargins(0, 0, 0, 0)
            self.w_main.__dict__[pname].setLayout(grid)

        # icon and window size
        self.w_main.setWindowIcon(QIcon('img/nelia-icon32.png'))
        self.w_main.setGeometry(100,70,1000,600)

        # initialize modules
        self.data.run['mainwindow'] = self
        self.data.run['config']     = NxConfig (data)
        self.data.run['project']    = NxProject(self, data, self.w_project)
        self.data.run['log']        = NxLog    (self, data, self.w_log)
        self.data.run['roadmap']    = NxRoadmap(self, data, self.w_roadmap)

        # Dissable all tabs except the project tab.
        # They show the data from the selected project, and are in undefined
        # before a selection is made.
        self.dissableTabs()

        # Connect signals and slots.
        self.w_main.tabnavi.currentChanged.connect(self.tabChanged)

        # Global shortcuts.
        close_shortcut = QShortcut(QKeySequence('Ctrl+w'), self.w_main)
        close_shortcut.activated.connect(self.w_main.close)
        switch_forward = QShortcut(QKeySequence('Ctrl+PgUp'), self.w_main)
        switch_forward.activated.connect(self.onTabForward)
        switch_backward = QShortcut(QKeySequence('Ctrl+PgDown'), self.w_main)
        switch_backward.activated.connect(self.onTabBackward)
        save = QShortcut(QKeySequence('Ctrl+s'), self.w_main)
        save.activated.connect(self.data.save)
        debug = QShortcut(QKeySequence('Ctrl+d'), self.w_main)
        debug.activated.connect(self.debug)

        # Intercept close event (see self.eventFilter).
        QObject.installEventFilter(self.w_main, self)
        signal.signal(signal.SIGTERM, self.onExit)

        self.applyConfig()
        self.data.run['project'].reset()

# ------------------------------------------------------------------------------
    def debug(self):

        home = os.path.expanduser('~')
        with open(os.path.join(home, '.cache', 'nelia.debug.py'), 'w') as f:
            f.write(pprint.pformat(self.data.__dict__))

    def updateConfig(self):

        """
            Update configuration details. This is mostly the column widths.
        """
        self.data.run['project'].saveLayout()
        self.data.run['log'].saveLayout()
        self.data.run['roadmap'].saveLayout()
        self.data.run['config'].config_data['project']['header_width'] = \
                self.data.run['project'].header_width
        self.data.run['config'].config_data['project']['sort_column'] = \
                self.data.run['project'].sort_column
        self.data.run['config'].config_data['project']['sort_order'] = \
                self.data.run['project'].sort_order.__repr__()
        self.data.run['config'].config_data['log']['header_width'] = \
                self.data.run['log'].header_width
        self.data.run['config'].config_data['log']['sort_column'] = \
                self.data.run['log'].sort_column
        self.data.run['config'].config_data['log']['sort_order'] = \
                self.data.run['log'].sort_order.__repr__()
        self.data.run['config'].config_data['roadmap']['header_width'] = \
                self.data.run['roadmap'].header_width
        self.data.run['config'].config_data['roadmap']['sort_column'] = \
                self.data.run['roadmap'].sort_column
        self.data.run['config'].config_data['roadmap']['sort_order'] = \
                self.data.run['roadmap'].sort_order.__repr__()

        x = self.data.run['config'].config_data['roadmap']
        x['show_feature'] = self.w_roadmap.check_feature.isChecked()
        x['show_issue'] = self.w_roadmap.check_issue.isChecked()
        x['show_open'] = self.w_roadmap.check_open.isChecked()
        x['show_closed'] = self.w_roadmap.check_closed.isChecked()
        x['show_low'] = self.w_roadmap.check_low.isChecked()
        x['show_medium'] = self.w_roadmap.check_medium.isChecked()
        x['show_high'] = self.w_roadmap.check_high.isChecked()
        x['show_core'] = self.w_roadmap.check_core.isChecked()
        x['show_auxiliary'] = self.w_roadmap.check_auxiliary.isChecked()
        x['show_security'] = self.w_roadmap.check_security.isChecked()
        x['show_corrective'] = self.w_roadmap.check_corrective.isChecked()
        x['show_architecture'] = self.w_roadmap.check_architecture.isChecked()
        x['show_refactor'] = self.w_roadmap.check_refactor.isChecked()

# ------------------------------------------------------------------------------
    def applyConfig(self):

        if self.data.run['config'].no_config == True:
            return

        self.data.run['project'].header_width = \
            self.data.run['config'].config_data['project']['header_width']
        self.data.run['project'].sort_column = \
            self.data.run['config'].config_data['project']['sort_column']
        if self.data.run['config'].config_data['project']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                self.data.run['project'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif self.data.run['config'].config_data['project']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                self.data.run['project'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        self.data.run['log'].header_width = \
            self.data.run['config'].config_data['log']['header_width']
        self.data.run['log'].sort_column = \
            self.data.run['config'].config_data['log']['sort_column']
        if self.data.run['config'].config_data['log']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                self.data.run['log'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif self.data.run['config'].config_data['log']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                self.data.run['log'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        self.data.run['roadmap'].header_width = \
            self.data.run['config'].config_data['roadmap']['header_width']
        self.data.run['roadmap'].sort_column = \
            self.data.run['config'].config_data['roadmap']['sort_column']
        if self.data.run['config'].config_data['roadmap']['sort_order'] \
           == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
                self.data.run['roadmap'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.DescendingOrder
        elif self.data.run['config'].config_data['roadmap']['sort_order'] \
                == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
                self.data.run['roadmap'].sort_order \
                        = PySide.QtCore.Qt.SortOrder.AscendingOrder
        self.data.run['project'].loadLayout()
        self.data.run['log'].loadLayout()
        self.data.run['roadmap'].loadLayout()

        x = self.data.run['config'].config_data['roadmap']

        if x['show_feature']:
            self.w_roadmap.check_feature.setChecked(True)
        else:
            self.w_roadmap.check_feature.setChecked(False)
        if x['show_issue']:
            self.w_roadmap.check_issue.setChecked(True)
        else:
            self.w_roadmap.check_issue.setChecked(False)
        if x['show_open']:
            self.w_roadmap.check_open.setChecked(True)
        else:
            self.w_roadmap.check_open.setChecked(False)
        if x['show_closed']:
            self.w_roadmap.check_closed.setChecked(True)
        else:
            self.w_roadmap.check_closed.setChecked(False)

        if x['show_low']:
            self.w_roadmap.check_low.setChecked(True)
        else:
            self.w_roadmap.check_low.setChecked(False)
        if x['show_medium']:
            self.w_roadmap.check_medium.setChecked(True)
        else:
            self.w_roadmap.check_medium.setChecked(False)
        if x['show_high']:
            self.w_roadmap.check_high.setChecked(True)
        else:
            self.w_roadmap.check_high.setChecked(False)

        if x['show_core']:
            self.w_roadmap.check_core.setChecked(True)
        else:
            self.w_roadmap.check_core.setChecked(False)
        if x['show_auxiliary']:
            self.w_roadmap.check_auxiliary.setChecked(True)
        else:
            self.w_roadmap.check_auxiliary.setChecked(False)
        if x['show_security']:
            self.w_roadmap.check_security.setChecked(True)
        else:
            self.w_roadmap.check_security.setChecked(False)
        if x['show_corrective']:
            self.w_roadmap.check_corrective.setChecked(True)
        else:
            self.w_roadmap.check_corrective.setChecked(False)
        if x['show_architecture']:
            self.w_roadmap.check_architecture.setChecked(True)
        else:
            self.w_roadmap.check_architecture.setChecked(False)
        if x['show_refactor']:
            self.w_roadmap.check_refactor.setChecked(True)
        else:
            self.w_roadmap.check_refactor.setChecked(False)

# ------------------------------------------------------------------------------
    def onExit(self, num, frame):
        """
        We want to shut down normally on SIGTERM too. This can happen when the
        computer is turned off, without closing the application first. This
        will issue the main window to close, which will trigger the event
        filter and shout down properly.
        """

        self.w_main.close()

# ------------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        """
        Capture main window close event.  This might be caused by the user
        clicking the (x) window button or by exiting via the Ctrl-w shortcut
        (or any other way that tells the main window to close).
        """

        if obj == self.w_main and isinstance(event, QCloseEvent):
            self.updateConfig()
            self.data.run['config'].writeConfig()
            self.data.save()
        res = False
        try:
            res = QObject.eventFilter(self.w_main, obj, event)
        except:
            pass
        return res

# ------------------------------------------------------------------------------
    def onTabForward(self):

        # get current tab index
        tab_index = self.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = self.w_main.tabnavi.count()

        # next tab
        if tab_index+1 == tab_count:
            self.w_main.tabnavi.setCurrentIndex(0)
        elif self.w_main.tabnavi.isTabEnabled(tab_index+1):
            self.w_main.tabnavi.setCurrentIndex(tab_index+1)

# ------------------------------------------------------------------------------
    def onTabBackward(self):

        # get current tab index
        tab_index = self.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = self.w_main.tabnavi.count()

        if tab_index == 0:
            if self.w_main.tabnavi.isTabEnabled(tab_count-1):
                self.w_main.tabnavi.setCurrentIndex(tab_count-1)
        else:
            self.w_main.tabnavi.setCurrentIndex(tab_index-1)

# ------------------------------------------------------------------------------
    def enableTabs(self):

        for i in range(1,3):
            self.w_main.tabnavi.setTabEnabled(i, True)

# ------------------------------------------------------------------------------
    def dissableTabs(self):

        for i in range(1,3):
            self.w_main.tabnavi.setTabEnabled(i, False)

# ------------------------------------------------------------------------------
    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.w_main.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == '&Log':
            self.data.run['log'].onShowTab()
        if cur_tab_name == '&Roadmap':
            self.data.run['roadmap'].onShowTab()

# ------------------------------------------------------------------------------

