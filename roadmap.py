#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxRoadmap(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        self.savdat = savdat
        self.rundat = rundat
        
        self.rundat['roadmap'] = {'last_pid': None}  # roadmap save base
        self.savdat['roadmap'] = {}

        # roadmap main widget, prefix: rmap == ui
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/roadmap.ui')
        uifile.open(QFile.ReadOnly)
        self.roadmap = loader.load(uifile)
        uifile.close()
        
        self.milestone_menu = QMenu(self.roadmap)
        self.roadmap.rmap_push_milestone.setMenu(self.milestone_menu)        
        
        parent_widget = self.rundat['mainwindow']['tab_roadmap']
        self.roadmap.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(self.roadmap, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)

        uifile = QFile('forms/roadmap_add_feature.ui')
        uifile.open(QFile.ReadOnly)
        self.add_feature = loader.load(uifile)
        uifile.close()
        self.add_feature.setParent(self.roadmap)
        self.add_feature.setWindowFlags(Qt.Dialog)

        self.rundat['roadmap'][':onShowTab'] = self.onShowTab

        self.rundat['roadmap']['feature_headers'] = \
            ['Name', 'Target', 'Prio.', 'Type', 'Compl.', 'ID']
        self.rundat['roadmap']['issue_headers'] = \
            ['Name', 'Target', 'Prio.', 'Sev.', 'Closed', 'ID']

        self.roadmap.rmap_push_add_feature.clicked.connect(self.showAddFeature)
        self.add_feature.accepted.connect(self.onSubmitNewFeature)
        
    ####################   METHODS   #################### 

    def onShowTab(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        # project selection changed or new project
        if self.rundat['roadmap']['last_pid'] == None \
                or self.rundat['roadmap']['last_pid'] != pid:

            # new pid, reset view!
            project_name = self.rundat['project'][':getSelectedProjectName']()
            self.roadmap.rmap_line_project.setText(project_name)
            self.add_feature.af_line_project.setText(project_name)

            # no roadmap for this pid yet
            if pid not in self.savdat['roadmap']:

                # new roadmap starts with version 0.1
                self.rundat['roadmap']['selected_milestone'] = (0,1)

                # create data skeleton and initiate first minor and major version
                self.savdat['roadmap'][pid] = {
                    'last_feature_id': 0,       # each feature has a unique id
                    'last_issue_id': 0,         # same goes for issues
                    'current_milestone': (0,0), # last completed milestone
                    # the next one is tricky:
                    # versions are calculated from index of the below lists
                    # outer list: major version, starting with 0
                    # inner list: minor version, starting with n.0, 
                    #             except the first, which starts with n.1
                    'versions' : [
                        [{'m': '0.1', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}],
                        [{'m': '1.0', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
                    ]
                }

            self.rundat['roadmap']['combo_labels'] = [] # store labels for combo boxes
            self.rundat['roadmap']['next_combo_index'] = 0 # index for next roadmap in combo boxes

            self.update_combos()

        self.add_feature.af_radio_secondary.setChecked(False)
        self.add_feature.af_radio_primary.setChecked(True)
        self.add_feature.af_spin_priority.setValue(50)

        # reset tables
        table = self.roadmap.rmap_table_features
        model = self.rundat['roadmap']['feature_table_model'] = QStandardItemModel()
        model.clear()

        model.setHorizontalHeaderLabels(self.rundat['roadmap']['feature_headers'])
        table.setModel(model)
        
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 50)
        table.setColumnWidth(3, 50)
        table.setColumnWidth(4, 68)
        table.setColumnWidth(5, 50)

        # TODO: POPULATE FEATURES TABLE ON TAB SWITCH

        table = self.roadmap.rmap_table_issues
        model = self.rundat['roadmap']['issue_table_model'] = QStandardItemModel()
        model.clear()
        
        model.setHorizontalHeaderLabels(self.rundat['roadmap']['issue_headers'])
        table.setModel(model)
        
        table.setColumnWidth(0, 200)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 50)
        table.setColumnWidth(3, 50)
        table.setColumnWidth(4, 68)
        table.setColumnWidth(5, 50)

        # TODO: POPULATE ISSUES TABLE ON TAB SWITCH

    def showAddFeature(self):
        
        self.add_feature.af_line_name.clear()
        self.add_feature.af_text_description.clear()
        self.add_feature.show()
    
    def onSubmitNewFeature(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        # prepare new feature data
        milestone = self.add_feature.af_combo_target.currentText()
        t_major, t_minor = milestone[1:milestone.find(' ')].split('.')
        t_major = int(t_major)
        t_minor = int(t_minor)
        ftype = None
        if self.add_feature.af_radio_primary.isChecked():
            ftype = 'primary'
        else:
            ftype = 'secondary'

        new_feature = {
            'name': self.add_feature.af_line_name.text(),
            'target': [t_major, t_minor],
            'priority': self.add_feature.af_spin_priority.value(),
            'type': ftype,
            'description': self.add_feature.af_text_description.toPlainText(),
            'created': int(time.time()),
            'completed': 0
        }

        # save new feature data
        last_feature_id = self.savdat['roadmap'][pid]['last_feature_id']
        self.savdat['roadmap'][pid][t_major][t_minor]['fo'][last_feature_id+1] = new_feature
        self.savdat['roadmap'][pid]['last_feature_id'] += 1


        '''
            0.1 -> 0.2
            1.0 -> 2.0, 1.1
        '''

        # create new milestone, if necessary
        if t_minor != 0 and t_major+1 in self.savdat['roadmap'][pid]: # minor milestone

            if t_minor+1 not in self.savdat['roadmap'][pid][t_major]: # next milestone does not exist yet
                
                self.savdat['roadmap'][pid][t_major][t_minor+1] = \
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
                   
        elif t_major+1 not in self.savdat['roadmap'][pid]: # next major milestone does not exist yet

            # x.1
            self.savdat['roadmap'][pid][t_major][1] = \
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
            # 1.x
            self.savdat['roadmap'][pid][t_major+1] = { 0:
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}}

        self.update_combos()

    def update_combos(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        rmap_push_milestone = self.roadmap.rmap_push_milestone
        root_menu = self.milestone_menu
        root_menu.clear()

        versions = self.savdat['roadmap'][pid]['versions']
        
        x, y = self.savdat['roadmap'][pid]['current_milestone']
        print('\nRUN WITH..\n', 'x:',x,'y:',y)

        ### DELTA CALCULATION ###
        # The following nested loop is somewhat hard to digest. It calculates
        # the major and minor deltas of each milestone version compared to the
        # current version. Δn is the difference of major versions, quite simple.
        # Δm is the challangeing part: it is the total difference of minor
        # milestone versions compared to the current one. E.g. If you are at
        # version 3.4, version 1 and two have 5 milestones each, then the minor
        # delta for 1.2 will be 2 + 5 + 4 = (-)11. Major will be -2 -> -2,12
        # See nelia/calculations/version-delta.py for detailed test.
        
        # FIXME: move this code to the mpushbutton class
        
        # loop through major versions
        Δn = 0
        for n in range(len(versions)):
            Δn = n - x
            major_menu = QMenu(self.roadmap)

            # loop through minor versions
            Δm = 0
            mfo = mfc = mio = mic = 0
            for m in range(len(versions[n])):
                
                action = QAction(major_menu)
                
                fo = len(versions[n][m]['fo'])
                fc = len(versions[n][m]['fc'])
                io = len(versions[n][m]['io'])
                ic = len(versions[n][m]['ic'])
                                
                # 0.x series starts with 0.1 instead of 0.0
                if n == 0:
                    m += 1

                # current version = 0.0 (no milestones reached)
                if x == 0 and y == 0:
                    if n == 0:
                        Δm = m
                    if n > 0:
                        Δm = sum(len(versions[s]) for s in range(n)) + m + 1
                # current version = 0.y, y>0
                if x == 0 and y > 0:
                    if n > 0:
                        Δm = sum(len(versions[s]) for s in range(1,n)) + m + len(versions[0]) - y + 1
                    else:
                        Δm = m - y
                # current version = 1.y, y>=0
                if x == 1:
                    if n == x:
                        Δm = m - y
                    if n > x:
                        Δm = sum(len(versions[s]) for s in range(x+1,n)) + m + len(versions[x]) - y
                    if n < x:
                        Δm = -1 * (y + (len(versions[0])-m))
                        if n == 0:
                            Δm -= 1
                # current major version > 1
                if x > 1:
                    if n == x:
                        Δm = m - y
                    if n > x:
                        Δm = sum(len(versions[s]) for s in range(x+1,n)) + m + len(versions[x]) - y
                    if n < x:
                        Δm = -1 * (
                            (  len(versions[n]) - m)
                             + sum(len(versions[s]) for s in range(n+1, x))
                             + y  )
                        if n == 0:
                            Δm -= 1

                # compute completion symbol
                if Δm > 1:
                    sign = '+'
                    icon = '◇'
                if Δm == 1:
                    sign = '+'
                    icon = '◈'
                if Δm == 0:
                    sign = ''
                    icon = '◆'
                if Δm < 0:
                    sign = '-'
                    icon = '◆'

                # compute major and minor version combined delta
                # notice how this has nothing to do with floating point
                # instead it's two deltas, major, and combined minor
                Δnm = '{}{},{}'.format(sign, abs(Δn), abs(Δm))



                mfo += fo
                mfc += fc
                mio += io
                mic += ic

                # TODO: compute features and issues
                action.setText('{}   v{}.{}   {}   f:{}/{}   i:{}/{}'.format(icon,n,m,Δnm,fo,fo+fc,io,io+ic))
                major_menu.addAction(action)

                print('n:',n,'m:',m,'\tΔn:',Δn,'Δm:',Δm,'\tΔnm:', Δnm, '\ticon:',icon)
            
            # FIXME: icon should be properly computed for major milestone
            major_menu.setTitle('{}   v{}.x   f:{}/{}   i:{}/{}'.format(
                icon, n, mfo, mfo+mfc, mio, mio+mic))
            root_menu.addMenu(major_menu)

        """
        self.rundat['roadmap']['combo_labels'] = []

        # compute next milestone (current +0.1 or +1.0 if no more minor milestones exist)
        next_milestone = [0,0]
        c_major, c_minor = self.savdat['roadmap'][pid]['current_milestone']
        if c_minor+1 in self.savdat['roadmap'][pid][c_major]:
            next_milestone = [c_major, c_minor+1]
        else:
            next_milestone = [c_major+1, 0]
        i = 0 # loop counter, used to determine next combo index

        # populate roadmap selection combo
        for major in self.savdat['roadmap'][pid]:
            # loop through major milestones
            if isinstance(major, int):
                # loop through minor milestones
                for minor in self.savdat['roadmap'][pid][major]:
                    ref = self.savdat['roadmap'][pid][major][minor] # reference to loop milestone
                    bref = self.savdat['roadmap'][pid] # referece to pid base

                    foc = len(ref['fo']) # number of open features
                    fcc = len(ref['fc']) # number of closed features
                    ioc = len(ref['io']) # number of open issues
                    icc = len(ref['ic']) # number of closed issues

                    # check if we are at next milestone and store index if so
                    if major == next_milestone[0] and minor == next_milestone[1]:
                        self.rundat['roadmap']['next_combo_index'] = i

                    # compute major and minor delta to current milestone
                    majd = major - bref['current_milestone'][0] # milestone delta
                    mind = 0
                    sign = '+'
                    # compute minor delta
                    if majd == 0:
                        mind = minor
                    elif majd > 0:
                        mind = minor - bref['current_milestone'][1]
                    else:
                        mind = bref['current_milestone'][1] + (len(bref[major]) - minor)
                        sign = '-'

                    # put together combo label for milestone
                    vname = 'v{}.{}   {}{}.{}   f:{}/{}   i:{}/{}'.format(
                        major, minor, sign, majd, mind, foc, fcc+foc, ioc, icc+ioc)

                    self.rundat['roadmap']['combo_labels'].append(vname)

                    i += 1 # advance loop counter

        # populate combo box labels
        self.roadmap.rmap_combo_milestone.clear()
        self.roadmap.rmap_combo_milestone.addItems(self.rundat['roadmap']['combo_labels'])
        self.roadmap.rmap_combo_milestone.setCurrentIndex(self.rundat['roadmap']['next_combo_index'])
        
        self.add_feature.af_combo_target.clear()
        self.add_feature.af_combo_target.addItems(self.rundat['roadmap']['combo_labels'])
        self.add_feature.af_combo_target.setCurrentIndex(self.rundat['roadmap']['next_combo_index'])

        from pprint import pprint
        pprint(self.savdat['roadmap'])
        """

    def reset(self, savdat):
    
        self.savdat = savdat

        # ensure roadmap is reloaded when switched to after opening
        self.rundat['roadmap']['last_pid'] = None


# vim: set ts=4 sw=4 ai si expandtab:

