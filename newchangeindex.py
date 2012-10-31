#! /usr/bin/env python3


"""
Application Name: 	Nelia
Component:			New/Change Index Entry

This file contains the dialog to create a new / change an 
existing project index entry.
"""

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools

class NewChangeIndex(QtCore.QObject):
    
    def __init__(self, index_table_ctrl):
        
        super().__init__()
        self.index_table_ctrl = index_table_ctrl

        loader = QtUiTools.QUiLoader()
        
        # NEW/CHANGE WIDGET SETUP
        uifile = QtCore.QFile('forms/newchangerootentry.ui')
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile)
        uifile.close()
        
        # CONNECT SIGNALS
        self.ui.push_create.clicked.connect(self.onCreateClick)
        self.ui.push_change.clicked.connect(self.onChangeClick)
        
    def showChange(self):

        table = self.index_table_ctrl
        model = table.model
        rowindex = table.currentIndex().row()

        # read the fields
        self.ui.line_name.setText(
            model.itemFromIndex(
            model.index(rowindex, 0)).text())
        
        self.ui.combo_entry_type.setCurrentIndex(
            self.ui.combo_entry_type.findText(
            model.itemFromIndex(
            model.index(rowindex, 1)).text()))

        self.ui.combo_category.setCurrentIndex(
            self.ui.combo_category.findText(
            model.itemFromIndex(
            model.index(rowindex, 3)).text()))

        self.ui.spin_priority.setValue(
            int(
            model.itemFromIndex(
            model.index(rowindex, 4)).text()))

        self.ui.spin_challenge.setValue(
            int(
            model.itemFromIndex(
            model.index(rowindex, 5)).text()))
        
        self.ui.push_create.hide()
        self.ui.push_change.show()

        self.ui.show()

    def showCreate(self):
        
        self.ui.line_name.clear()
        self.ui.combo_entry_type.setCurrentIndex(0)
        self.ui.combo_category.setCurrentIndex(0)
        self.ui.spin_priority.setValue(0)
        self.ui.spin_challenge.setValue(0)

        self.ui.push_create.show()
        self.ui.push_change.hide()

        self.ui.show()

    def onCreateClick(self):

        table = self.index_table_ctrl

        table.addNewRow(
            self.ui.line_name.text(), self.ui.combo_entry_type.currentText(),
            self.ui.combo_category.currentText(), 
            self.ui.spin_priority.value(), self.ui.spin_challenge.value())

        self.ui.hide()

    def onChangeClick(self):

        table = self.index_table_ctrl
        model = table.model
        rowindex = table.currentIndex().row()

        itemid = int(model.itemFromIndex(
            model.index(rowindex, 8)).text())

        table.changeRow(itemid, rowindex,
            self.ui.line_name.text(), self.ui.combo_entry_type.currentText(),
            self.ui.combo_category.currentText(), 
            self.ui.spin_priority.value(), self.ui.spin_challenge.value())

        self.ui.hide()


# vim: set ts=4 sw=4 ai si expandtab:

