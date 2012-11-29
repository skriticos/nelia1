#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from pprint import pprint
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton

class NxRoadmap(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        self.rundat = rundat

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

        if 'roadmap' not in  self.rundat:
            self.rundat['roadmap'] = {}
        self.rundat['roadmap'][':onShowTab'] = self.onShowTab

        self.rundat['roadmap']['feature_headers'] = \
            ['Name', 'Target', 'Prio.', 'Type', 'Compl.', 'ID']
        self.rundat['roadmap']['issue_headers'] = \
            ['Name', 'Target', 'Prio.', 'Sev.', 'Closed', 'ID']

        self.roadmap.rmap_push_add_feature.clicked.connect(self.showAddFeature)
        self.add_feature.accepted.connect(self.onSubmitNewFeature)

        self.reset(savdat)
        self.savdat['roadmap'] = {}
        
    ####################   METHODS   #################### 

    def onChangeVersionSelection(self, x, y, current_text):

        self.selected_x = x
        self.selected_y = y

        # TODO: reload feature / issue tables

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


        # create MPushButton widget
        x, y = self.savdat['roadmap'][pid]['current_milestone']
        versions = self.savdat['roadmap'][pid]['versions']

        self.roadmap.gridLayout_2.removeWidget(self.roadmap.rmap_push_milestone)
        self.roadmap.rmap_push_milestone.close()
        self.roadmap.rmap_push_milestone = MPushButton(x, y, versions, self.roadmap, self.onChangeVersionSelection)
        self.roadmap.gridLayout_2.addWidget(self.roadmap.rmap_push_milestone, 0, 1, 1, 1)
        self.roadmap.label_2.setBuddy(self.roadmap.rmap_push_milestone)
        
        self.selected_x, self.selected_y = self.roadmap.rmap_push_milestone.getVersion() 
        
        # reset controls
        self.add_feature.af_radio_secondary.setChecked(False)
        self.add_feature.af_radio_primary.setChecked(True)
        self.add_feature.af_spin_priority.setValue(50)

        # reset tables
        table = self.roadmap.rmap_table_features
        model = self.rundat['roadmap']['feature_table_model'] = QStandardItemModel()
        model.clear()

        model.setHorizontalHeaderLabels(self.rundat['roadmap']['feature_headers'])
        table.setModel(model)
        
        table.setColumnWidth(0, 180)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 50)
        table.setColumnWidth(3, 70)
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

        pid = self.rundat['project'][':getSelectedProject']()
        x, y = self.savdat['roadmap'][pid]['current_milestone']
        versions = self.savdat['roadmap'][pid]['versions']

        self.add_feature.gridLayout_2.removeWidget(self.add_feature.push_target_milestone)
        self.add_feature.push_target_milestone.close()
        self.add_feature.push_target_milestone = MPushButton(x,y,versions,self.add_feature,None,self.selected_x,self.selected_y)
        self.add_feature.gridLayout_2.addWidget(self.add_feature.push_target_milestone, 1, 1, 1, 1);

        self.add_feature.af_line_name.clear()
        self.add_feature.af_text_description.clear()
        self.add_feature.show()
    
    def onSubmitNewFeature(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        # prepare new feature data
        milestone = self.add_feature.push_target_milestone.text()
        x, y = milestone.split(' ')[3][1:].split('.')
        versions = self.savdat['roadmap'][pid]['versions']
        
        x = int(x)
        y = int(y)

        ftype = None
        if self.add_feature.af_radio_primary.isChecked():
            ftype = 'Primary'
        else:
            ftype = 'Secondary'

        name = self.add_feature.af_line_name.text()
        priority = self.add_feature.af_spin_priority.value()
        description = self.add_feature.af_text_description.toPlainText()

        new_feature = {
            'name': self.add_feature.af_line_name.text(),
            'priority': self.add_feature.af_spin_priority.value(),
            'type': ftype,
            'description': self.add_feature.af_text_description.toPlainText(),
            'created': int(time.time()),
            'completed': 0
        }
        
        last_feature_id = self.savdat['roadmap'][pid]['last_feature_id']

        # only add feature, if added to currently selected version
        if x == self.selected_x and y == self.selected_y:
            # add to feature table
            model = self.rundat['roadmap']['feature_table_model']
            model.insertRow(0, [
                QStandardItem(name),
                QStandardItem('{}.{}'.format(x,y)),
                QStandardItem(str(priority)),
                QStandardItem(ftype),
                QStandardItem('No'),
                QStandardItem(str(last_feature_id+1))
            ])

        # save new feature data
        if x == 0:
            y -= 1

        if len(versions) == x+1: # new major version
            pass
        elif len(versions[x]) == y+1: # new minor version
            versions.append({'m': '{}.{}'.format(x, y+2), 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}),
        

        '''
            0.1 -> 0.2
            1.0 -> 2.0, 1.1

        # create new milestone, if necessary
        if y != 0 and x+1 in self.savdat['roadmap'][pid]: # minor milestone

            if y+1 not in self.savdat['roadmap'][pid][x]: # next milestone does not exist yet
                
                self.savdat['roadmap'][pid][x][y+1] = \
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
                   
        elif x+1 not in self.savdat['roadmap'][pid]: # next major milestone does not exist yet

            # x.1
            self.savdat['roadmap'][pid][x][1] = \
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
            # 1.x
            self.savdat['roadmap'][pid][x+1] = { 0:
                    {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}}
        '''

        self.savdat['roadmap'][pid]['versions'][x][y]['fo'][last_feature_id+1] = new_feature
        self.savdat['roadmap'][pid]['last_feature_id'] += 1

        # update roadmap widget milestone selector
        x, y = self.savdat['roadmap'][pid]['current_milestone']

        self.roadmap.gridLayout_2.removeWidget(self.roadmap.rmap_push_milestone)
        self.roadmap.rmap_push_milestone.close()
        self.roadmap.rmap_push_milestone = MPushButton(x, y, versions, self.roadmap, self.onChangeVersionSelection, self.selected_x, self.selected_y)
        self.roadmap.gridLayout_2.addWidget(self.roadmap.rmap_push_milestone, 0, 1, 1, 1)
        self.roadmap.label_2.setBuddy(self.roadmap.rmap_push_milestone)

    def reset(self, savdat):
    
        self.savdat = savdat

        # ensure roadmap is reloaded when switched to after opening
        self.rundat['roadmap']['last_pid'] = None


# vim: set ts=4 sw=4 ai si expandtab:

