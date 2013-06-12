# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MPushButton(QPushButton):
    change_signal = Signal((int, int))
    def __init__(self, parent=None, sel_x=None, sel_y=None, open_only=False):
        super().__init__(parent)
        x = dc.sp.curr.major.v
        y = dc.sp.curr.minor.v
        self.setText('        no data        ')
        self.root_menu = QMenu(self)
        self.setMenu(self.root_menu)
        Δn = 0
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for n in dc.sp.m.idx.v: # n == major verions
            Δn = n - x
            major_menu = QMenu(self)
            Δm = 0
            mfo = mfc = mio = mic = 0 # reset major version feature counters
            for m in dc.sp.m._(n).idx.v: # m == minor versions
                action = QAction(self)
                fo = fc = io = ic = 0
                for miid in dc.sp.m._(n)._(m).idx.v:
                    if dc.sp.mi._(miid).itype.v == 'Feature':
                        if dc.sp.mi._(miid).status.v == 'Open':
                            fo += 1
                        else:
                            fc += 1
                    elif dc.sp.mi._(miid).itype.v == 'Issue':
                        if dc.sp.mi._(miid).status.v == 'Open':
                            io += 1
                        else:
                            ic += 1
                mfo += fo
                mfc += fc
                mio += io
                mic += ic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if x == 0 and y == 1:
                    if n == 0:
                        Δm = m
                    if n > 0:
                        Δm = sum(len(dc.sp.m._(s).idx.v) for s in range(n)) \
                            + m + 1
                if x == 0 and y > 1:
                    if n == 0:
                        Δm = m - y + 1
                    if n > 0:
                        Δm = sum(len(dc.sp.m._(s).idx.v) for s in range(1,n)) \
                            + m + len(dc.sp.m._(0).idx.v) - y + 2
                if x == 1:
                    if n == 0:
                        Δm = -1 * (y + (len(dc.sp.m._(0).idx.v) - m))
                    if n == x:
                        Δm = m - y + 1
                    if n > x:
                        Δm = sum(len(dc.sp.m._(s).idx.v) for s in range(x+1,n))\
                            + m + len(dc.sp.m._(x).idx.v) - y + 1
                if x > 1:
                    if n < x:
                        Δm = -1 * ((len(dc.sp.m._(n).idx.v) - m)
                            + sum(len(dc.sp.m._(s).idx.v) for s in range(n+1,x))
                            + y + 1)
                        if n == 0:
                            Δm -= 1
                    if n == x:
                        Δm = m - y + 1
                    if n > x:
                        Δm = sum(len(dc.sp.m._(s).idx.v) for s in range(x+1,n))\
                            + m + len(dc.sp.m._(x).idx.v) - y + 1
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                oo = False
                if Δm > 1:
                    sign = '+'
                    icon = '◇'
                    oo = True
                if Δm == 1:
                    sign = '+'
                    icon = '◈'
                    oo = True
                    self.next_x = n
                    self.next_y = m
                if Δm == 0:
                    sign = ''
                    icon = '◆'
                if Δm < 0:
                    sign = '-'
                    icon = '◆'
                if open_only and not oo:
                    continue
                Δnm = '{}{},{}'.format(sign, abs(Δn), abs(Δm))
                label = '{}   v{}.{}   {}   f:{}/{}   i:{}/{}'.format(
                    icon,n,m,Δnm,fc,fo+fc,ic,io+ic)
                if sel_x == n and sel_y == m and open_only and Δm > 0:
                    self.setText(label)
                    self.current_text = label
                elif sel_x == n and sel_y == m and not open_only:
                    self.setText(label)
                    self.current_text = label
                elif Δm == 1:
                    self.setText(label)
                    self.current_text = label
                action.setText(label)
                action.triggered.connect(self.onSelectionChanged)
                major_menu.addAction(action)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            oo = False
            if Δn > 0:
                icon = '◇'
                oo = True
            if Δn == 0:
                icon = '◈'
                oo = True
            if Δn < 0:
                icon = '◆'
            if open_only and not oo:
                major_menu.close()
                continue
            title = '{}   v{}.x   f:{}/{}   i:{}/{}'\
                    .format(icon, n, mfc, mfo+mfc, mic, mio+mic)
            major_menu.setTitle(title)
            self.root_menu.addMenu(major_menu)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getVersion(self):
            x, y = self.current_text.split(' ')[3][1:].split('.')
            return int(x), int(y)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChanged(self):
        old_text = self.text()
        self.current_text = self.sender().text()
        if old_text == self.current_text: return
        self.setText(self.current_text)
        x, y = self.getVersion()
        self.change_signal.emit(x, y)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

