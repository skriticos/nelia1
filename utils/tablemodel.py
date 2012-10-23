#! /usr/bin/env python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *


"""
    Create a table model from a two dimensional array, 
    first element being the header.
"""
class TableModel(QStandardItemModel):

    def __init__(self):
        super().__init__()
    
    def setMatrix(self, matrix):

        self.setColumnCount(len(matrix[0]))
        for (i,colHeader) in enumerate(matrix[0]):
            self.setHeaderData(i, Qt.Horizontal, colHeader)

        for (i,row) in enumerate(matrix[1:]):
            self.insertRow(i)
            for (j,cell) in enumerate(row):
                self.setData(self.index(i,j), cell)

if __name__ == '__main__':

    print('Running test..')
    
    matrix=[['Col 1','Col 2','Col 3'],
            ['A1','A2','A3'],
            ['B1','B2','b3']]

    application = QApplication(sys.argv) 
    mainwindow = QMainWindow()

    model = TableModel()
    model.setMatrix(matrix)

    mainlisting = QTableView()
    mainlisting.setSortingEnabled(True)
    mainlisting.setModel(model)
    mainlisting.setEditTriggers(QAbstractItemView.NoEditTriggers)
    mainwindow.setCentralWidget(mainlisting)
    mainwindow.show()
    sys.exit(application.exec_())


# vim: set ts=4 sw=4 ai si expandtab:

