#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
import sys

app = QApplication(sys.argv)
mw = QMainWindow()

# create combo with three items
cb = QComboBox()
mw.setCentralWidget(cb)
cb.addItems(['foo','bar','baz'])

# print selected index
print (cb.currentIndex())

# print selected label
print (cb.currentText())

# connect changed
def changed(idx):
	print (idx)
	print (cb.currentText())
	print ('changed')

# connect changed signal
cb.currentIndexChanged.connect(changed)

# insert and delete item (index based)
cb.insertItem(1, 'new item')
cb.removeItem(0)

mw.show()
sys.exit(app.exec_())

