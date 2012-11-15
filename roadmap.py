#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

"""
roadmap prefixes:
    rmap = roadmap widget
    rmm  = roadmap milestone manage
    fil  = generic feature/issue list
    af   = add feature
    ai   = add issue
    ef   = edit feature
    ei   = edit issue
"""

class NxRoadmap(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat
        
        rd['modules'].append('roadmap')
        rd['roadmap'] = {}

        sd['roadmap'] = {}          # roadmap save base
        sd['roadmap']['p'] = {}     # roadmap for projects
        rd['roadmap']['last_roadmap_pid'] = None    # to check if reload roadmap on tab change necessary

        run_roadmap = rd['roadmap']
        sav_roadmap = sd['roadmap']

        # mainwindow widget setup
        loader = QtUiTools.QUiLoader()

        # pre-populate data index
        run_roadmap['self'] = self

        run_roadmap[':reset'] = self.reset
        run_roadmap[':onShowTab'] = self.onShowTab

        # add feature, prefix: af
        uifile = QFile('forms/roadmap_add_feature.ui')
        uifile.open(QFile.ReadOnly)
        af = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['af'] = af
        self.rundat['roadmap']['af_combo_target'] = af.af_combo_target
        self.rundat['roadmap']['af_line_name'] = af.af_line_name
        self.rundat['roadmap']['af_line_project'] = af.af_line_project
        self.rundat['roadmap']['af_radio_primary'] = af.af_radio_primary
        self.rundat['roadmap']['af_radio_secondary'] = af.af_radio_secondary
        self.rundat['roadmap']['af_spin_priority'] = af.af_spin_priority
        self.rundat['roadmap']['af_text_description'] = af.af_text_description

        # add issue, prefix: ai
        uifile = QFile('forms/roadmap_add_issue.ui')
        uifile.open(QFile.ReadOnly)
        ai = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['ai'] = ai
        self.rundat['roadmap']['ai_combo_low'] = ai.ai_combo_low
        self.rundat['roadmap']['ai_combo_medium'] = ai.ai_combo_medium
        self.rundat['roadmap']['ai_combo_target'] = ai.ai_combo_target
        self.rundat['roadmap']['ai_line_name'] = ai.ai_line_name
        self.rundat['roadmap']['ai_line_project'] = ai.ai_line_project
        self.rundat['roadmap']['ai_radio_critical'] = ai.ai_radio_critical
        self.rundat['roadmap']['ai_radio_high'] = ai.ai_radio_high
        self.rundat['roadmap']['ai_spin_priority'] = ai.ai_spin_priority
        self.rundat['roadmap']['ai_text_description'] = ai.ai_text_description

        # edit feature, prefix: ef
        uifile = QFile('forms/roadmap_edit_feature.ui')
        uifile.open(QFile.ReadOnly)
        ef = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['ef'] = ef
        self.rundat['roadmap']['ef_combo_target'] = ef.ef_combo_target
        self.rundat['roadmap']['ef_line_name'] = ef.ef_line_name
        self.rundat['roadmap']['ef_line_project'] = ef.ef_line_project
        self.rundat['roadmap']['ef_push_note_add'] = ef.ef_push_note_add
        self.rundat['roadmap']['ef_radio_primary'] = ef.ef_radio_primary
        self.rundat['roadmap']['ef_radio_secondary'] = ef.ef_radio_secondary
        self.rundat['roadmap']['ef_spin_priority'] = ef.ef_spin_priority
        self.rundat['roadmap']['ef_text_description'] = ef.ef_text_description
        self.rundat['roadmap']['ef_text_description'] = ef.ef_text_description
        self.rundat['roadmap']['ef_text_note_add'] = ef.ef_text_note_add
        self.rundat['roadmap']['ef_text_note_history'] = ef.ef_text_note_history

        # edit issue, prefix: ei
        uifile = QFile('forms/roadmap_edit_issue.ui')
        uifile.open(QFile.ReadOnly)
        ei = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['ei'] = ei
        self.rundat['roadmap']['ei_combo_low'] = ei.ei_combo_low
        self.rundat['roadmap']['ei_combo_medium'] = ei.ei_combo_medium
        self.rundat['roadmap']['ei_combo_target'] = ei.ei_combo_target
        self.rundat['roadmap']['ei_line_name'] = ei.ei_line_name
        self.rundat['roadmap']['ei_line_project'] = ei.ei_line_project
        self.rundat['roadmap']['ei_push_note_add'] = ei.ei_push_note_add
        self.rundat['roadmap']['ei_radio_critical'] = ei.ei_radio_critical
        self.rundat['roadmap']['ei_radio_high'] = ei.ei_radio_high
        self.rundat['roadmap']['ei_spin_priority'] = ei.ei_spin_priority
        self.rundat['roadmap']['ei_text_note_add'] = ei.ei_text_note_add
        self.rundat['roadmap']['ei_text_note_history'] = ei.ei_text_note_history

        # listing, prefix: fil
        uifile = QFile('forms/roadmap_listing.ui')
        uifile.open(QFile.ReadOnly)
        fil = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['fil'] = fil
        self.rundat['roadmap']['fil_line_project'] = fil.fil_line_project
        self.rundat['roadmap']['fil_push_delete'] = fil.fil_push_delete
        self.rundat['roadmap']['fil_push_edit'] = fil.fil_push_edit
        self.rundat['roadmap']['fil_table_item_list'] = fil.fil_table_item_list
        self.rundat['roadmap']['fil_text_description'] = fil.fil_text_description

        # roadmap main widget, prefix: rmap == ui
        uifile = QFile('forms/roadmap.ui')
        uifile.open(QFile.ReadOnly)
        rmap = loader.load(uifile)
        uifile.close()

        parent_widget = rd['mainwindow']['tab_roadmap']
        rmap.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(rmap, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)
        
        self.rundat['roadmap']['rmap'] = rmap
        self.rundat['roadmap']['rmap_combo_milestone'] = rmap.rmap_combo_milestone
        self.rundat['roadmap']['rmap_line_milestone_completed'] = rmap.rmap_line_milestone_completed
        self.rundat['roadmap']['rmap_line_milestone_next'] = rmap.rmap_line_milestone_next
        self.rundat['roadmap']['rmap_line_milestone_sum'] = rmap.rmap_line_milestone_sum
        self.rundat['roadmap']['rmap_line_project'] = rmap.rmap_line_project
        self.rundat['roadmap']['rmap_push_add_feature'] = rmap.rmap_push_add_feature
        self.rundat['roadmap']['rmap_push_add_issue'] = rmap.rmap_push_add_issue
        self.rundat['roadmap']['rmap_push_all_feature_close'] = rmap.rmap_push_all_feature_close
        self.rundat['roadmap']['rmap_push_all_feature_open'] = rmap.rmap_push_all_feature_open
        self.rundat['roadmap']['rmap_push_all_issue_close'] = rmap.rmap_push_all_issue_close
        self.rundat['roadmap']['rmap_push_all_issue_open'] = rmap.rmap_push_all_issue_open
        self.rundat['roadmap']['rmap_push_closed_features'] = rmap.rmap_push_closed_features
        self.rundat['roadmap']['rmap_push_closed_issues'] = rmap.rmap_push_closed_issues
        self.rundat['roadmap']['rmap_push_delete_feature'] = rmap.rmap_push_delete_feature
        self.rundat['roadmap']['rmap_push_delete_issue'] = rmap.rmap_push_delete_issue
        self.rundat['roadmap']['rmap_push_edit_feature'] = rmap.rmap_push_edit_feature
        self.rundat['roadmap']['rmap_push_edit_issue'] = rmap.rmap_push_edit_issue
        self.rundat['roadmap']['rmap_push_manage_milestone'] = rmap.rmap_push_manage_milestone
        self.rundat['roadmap']['rmap_push_open_features'] = rmap.rmap_push_open_features
        self.rundat['roadmap']['rmap_push_open_issues'] = rmap.rmap_push_open_issues
        self.rundat['roadmap']['rmap_table_open_features'] = rmap.rmap_table_open_features
        self.rundat['roadmap']['rmap_table_open_issues'] = rmap.rmap_table_open_issues

        # manage milestone, prefix: rmm
        uifile = QFile('forms/roadmap_manage_milestones.ui')
        uifile.open(QFile.ReadOnly)
        rmm = loader.load(uifile)
        uifile.close()

        self.rundat['roadmap']['rmm'] = rmm
        self.rundat['roadmap']['rmm_combo_parent'] = rmm.rmm_combo_parent
        self.rundat['roadmap']['rmm_line_custom'] = rmm.rmm_line_custom
        self.rundat['roadmap']['rmm_line_project'] = rmm.rmm_line_project
        self.rundat['roadmap']['rmm_push_add'] = rmm.rmm_push_add
        self.rundat['roadmap']['rmm_push_delete'] = rmm.rmm_push_delete
        self.rundat['roadmap']['rmm_push_move_down'] = rmm.rmm_push_move_down
        self.rundat['roadmap']['rmm_push_move_up'] = rmm.rmm_push_move_up
        self.rundat['roadmap']['rmm_radio_custom'] = rmm.rmm_radio_custom
        self.rundat['roadmap']['rmm_radio_mmp'] = rmm.rmm_radio_mmp
        self.rundat['roadmap']['rmm_spin_major'] = rmm.rmm_spin_major
        self.rundat['roadmap']['rmm_spin_minor'] = rmm.rmm_spin_minor
        self.rundat['roadmap']['rmm_spin_patch'] = rmm.rmm_spin_patch
        self.rundat['roadmap']['rmm_table_milestones'] = rmm.rmm_table_milestones
       
        # config
        rmm.setParent(self.rundat['mainwindow']['ui'])
        rmm.setWindowFlags(Qt.Dialog)
        af.setParent(self.rundat['mainwindow']['ui'])
        af.setWindowFlags(Qt.Dialog)
        ai.setParent(self.rundat['mainwindow']['ui'])
        ai.setWindowFlags(Qt.Dialog)
        ef.setParent(self.rundat['mainwindow']['ui'])
        ef.setWindowFlags(Qt.Dialog)
        ei.setParent(self.rundat['mainwindow']['ui'])
        ei.setWindowFlags(Qt.Dialog)
        fil.setParent(self.rundat['mainwindow']['ui'])
        fil.setWindowFlags(Qt.Dialog)

        # methods (pushbuttons)
        self.rundat['roadmap'][':onManageMilestoneClick'] = self.onManageMilestoneClick
        self.rundat['roadmap'][':onAddFeatureClick'] = self.onAddFeatureClick
        self.rundat['roadmap'][':onAddIssueClick'] = self.onAddIssueClick
        self.rundat['roadmap'][':onEditFeatureClick'] = self.onEditFeatureClick
        self.rundat['roadmap'][':onEditIssueClick'] = self.onEditIssueClick
        self.rundat['roadmap'][':onDeleteFeature'] = self.onDeleteFeature
        self.rundat['roadmap'][':onDeleteIssue'] = self.onDeleteIssue
        self.rundat['roadmap'][':onSelectedFeatureOpen'] = self.onSelectedFeatureOpen
        self.rundat['roadmap'][':onSelectedFeatureClosed'] = self.onSelectedFeatureClosed
        self.rundat['roadmap'][':onSelectedIssueOpen'] = self.onSelectedIssueOpen
        self.rundat['roadmap'][':onSelectedIssueClosed'] = self.onSelectedIssueClosed
        self.rundat['roadmap'][':onAllFeatureOpen'] = self.onAllFeatureOpen
        self.rundat['roadmap'][':onAllFetaureClose'] = self.onAllFetaureClose
        self.rundat['roadmap'][':onAllIssueOpen'] = self.onAllIssueOpen
        self.rundat['roadmap'][':onAllIssueClosed'] = self.onAllIssueClosed

        # CALLBACKS
        self.rundat['roadmap']['rmap_push_manage_milestone'].clicked.connect(
            self.rundat['roadmap'][':onManageMilestoneClick'])
        self.rundat['roadmap']['rmap_push_add_feature'].clicked.connect(
            self.rundat['roadmap'][':onAddFeatureClick'])
        self.rundat['roadmap']['rmap_push_add_issue'].clicked.connect(
            self.rundat['roadmap'][':onAddIssueClick'])
        self.rundat['roadmap']['rmap_push_edit_feature'].clicked.connect(
            self.rundat['roadmap'][':onEditFeatureClick'])
        self.rundat['roadmap']['rmap_push_edit_issue'].clicked.connect(
            self.rundat['roadmap'][':onEditIssueClick'])
        self.rundat['roadmap']['rmap_push_delete_feature'].clicked.connect(
            self.rundat['roadmap'][':onDeleteFeature'])
        self.rundat['roadmap']['rmap_push_open_features'].clicked.connect(
            self.rundat['roadmap'][':onSelectedFeatureOpen'])
        self.rundat['roadmap']['rmap_push_closed_features'].clicked.connect(
            self.rundat['roadmap'][':onSelectedFeatureClosed'])
        self.rundat['roadmap']['rmap_push_open_issues'].clicked.connect(
            self.rundat['roadmap'][':onSelectedIssueOpen'])
        self.rundat['roadmap']['rmap_push_closed_issues'].clicked.connect(
            self.rundat['roadmap'][':onSelectedIssueClosed'])
        self.rundat['roadmap']['rmap_push_all_feature_open'].clicked.connect(
            self.rundat['roadmap'][':onAllFeatureOpen'])
        self.rundat['roadmap']['rmap_push_all_feature_close'].clicked.connect(
            self.rundat['roadmap'][':onAllFetaureClose'])
        self.rundat['roadmap']['rmap_push_all_issue_open'].clicked.connect(
            self.rundat['roadmap'][':onAllIssueOpen'])
        self.rundat['roadmap']['rmap_push_all_issue_close'].clicked.connect(
            self.rundat['roadmap'][':onAllIssueClosed'])
        
    ####################   METHODS   #################### 
    def onShowTab(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        if self.rundat['roadmap']['last_roadmap_pid'] == None \
                or self.rundat['roadmap']['last_roadmap_pid'] != pid:

            self.rundat['roadmap']['selected_milestone_delta'] = 1

            # create pid data if not already done
            if pid not in self.savdat['roadmap']['p']:
                # create container for project
                self.savdat['roadmap']['p'][pid] = {}
                # setup features and issues
                self.savdat['roadmap']['p'][pid]['feature'] = {}
                self.savdat['roadmap']['p'][pid]['feature']['nextfeature'] = 0
                self.savdat['roadmap']['p'][pid]['feature']['f'] = {}
                self.savdat['roadmap']['p'][pid]['issue'] = {}
                self.savdat['roadmap']['p'][pid]['issue']['nextissue'] = 0
                self.savdat['roadmap']['p'][pid]['issue']['i'] = {}
                #  setup milestone
                self.savdat['roadmap']['p'][pid]['milestone'] = {}
                self.savdat['roadmap']['p'][pid]['milestone']['current'] = 0 # no milestone reached yet
                self.savdat['roadmap']['p'][pid]['milestone']['nextmilestone'] = 2
                self.savdat['roadmap']['p'][pid]['milestone']['m'] = {}
                #  setup first milestone
                self.savdat['roadmap']['p'][pid]['milestone']['m'][1] = {}
                self.savdat['roadmap']['p'][pid]['milestone']['m'][1]['name'] = '0.0.1'
                self.savdat['roadmap']['p'][pid]['milestone']['m'][1]['fid'] = set() # list of feature ids
                self.savdat['roadmap']['p'][pid]['milestone']['m'][1]['iid'] = set() # list of issue ids

            # new pid, reset view!
            project_name = self.rundat['project'][':getSelectedProjectName']()

            self.rundat['roadmap']['rmap_line_project'].setText(project_name)
            self.rundat['roadmap']['rmm_line_project'].setText(project_name)
            self.rundat['roadmap']['af_line_project'].setText(project_name)
            self.rundat['roadmap']['ef_line_project'].setText(project_name)
            self.rundat['roadmap']['ai_line_project'].setText(project_name)
            self.rundat['roadmap']['ei_line_project'].setText(project_name)
            self.rundat['roadmap']['fil_line_project'].setText(project_name)

            # process milestone list (update widgets)
            # #1: rmap_combo_milestone
            # #2: rmm_combo_parent
            # #3: rmm_table_milestones
            # #4: rmap_push_open_features
            # #5: rmap_push_open_issues
            # #6: rmap_push_closed_features
            # #7: rmap_push_closed_issues
            smref = self.savdat['roadmap']['p'][pid]['milestone']
            rmref = self.rundat['roadmap']
            rmref['selected'] = smref['current'] + 1 # the currently selected milestone (next by default)

            # iterate through milestones
            items = []
            current = smref['current'] # int
            index_of_next = 0
            for idx in range(1, smref['nextmilestone']):
                item_name = smref['m'][idx]['name']
                item_name += '   ('
                if idx > current:
                    item_name += '+'
                    item_name += str(idx-current)
                    if idx-current == 1:
                        item_name += ', next'
                        index_of_next = idx-1
                    item_name += ')'
                elif idx == current:
                    item_name += '+0, current)'
                else:
                    item_name += '-'
                    item_name += str(current-idx)
                    item_name += ')'
                items.append(item_name)
            self.rundat['roadmap']['rmap_combo_milestone'].clear()
            self.rundat['roadmap']['rmap_combo_milestone'].addItems(items)
            self.rundat['roadmap']['rmap_combo_milestone'].setCurrentIndex(index_of_next)

    def reset(self):
    
        # ensure roadmap is reloaded when switched to after opening
        self.rundat['roadmap']['last_roadmap_pid'] = None


    ####################   CALLBACKS   #################### 
    def onManageMilestoneClick(self):

        self.rundat['roadmap']['rmm'].show()

    def onAddFeatureClick(self):
        
        self.rundat['roadmap']['af'].show()

    def onAddIssueClick(self):

        self.rundat['roadmap']['ai'].show()

    def onEditFeatureClick(self):

        self.rundat['roadmap']['ef'].show()

    def onEditIssueClick(self):

        self.rundat['roadmap']['ei'].show()

    def onDeleteFeature(self):
        pass
    def onDeleteIssue(self):
        pass

    def onSelectedFeatureOpen(self):
        pass
    def onSelectedFeatureClosed(self):
        pass
    def onSelectedIssueOpen(self):
        pass
    def onSelectedIssueClosed(self):
        pass
    def onAllFeatureOpen(self):
        pass
    def onAllFetaureClose(self):
        pass
    def onAllIssueOpen(self):
        pass
    def onAllIssueClosed(self):
        pass

# vim: set ts=4 sw=4 ai si expandtab:

