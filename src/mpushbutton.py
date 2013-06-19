# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MPushButton(QPushButton):
    # signal is emited when the button selection is changed
    change_signal = Signal((int, int))
    # sel_x, sel_y → the selected version on the face
    # open_only →  ??
    def __init__(self, parent=None, sel_x=None, sel_y=None, open_only=False):
        super().__init__(parent)
        self.root_menu = QMenu(self)
        self.setMenu(self.root_menu)
        print()
        print('cmajor, cminor', dc.sp.curr.major.v, dc.sp.curr.minor.v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # iterate through major versions
        for loop_major in dc.sp.m.idx.v:
            loop_major_menu = QMenu(self)
            # count of major milestone items by type and status
            # m: major, f: feature, i: issue, c: closed, o: open
            mfo = mfc = mio = mic = 0
            # example dc.sp.curr.major.v = 1:
            #  loop_major 0: Δ_major →  0 - 1 = -1
            #  loop_major 1: Δ_major →  1 - 1 = 0
            #  loop_major 2: Δ_major →  2 - 1 = 1
            Δ_major = loop_major - dc.sp.curr.major.v
            # iterate through minor versions
            for loop_minor in dc.sp.m._(loop_major).idx.v:
                action = QAction(self)
                # count of minor milestone items by type and status
                fo = fc = io = ic = 0
                # iterate through items in minor milestone, count items by type
                # and status
                for miid in dc.sp.m._(loop_major)._(loop_minor).idx.v:
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
                # add them to the major milestone counter (looping through)
                mfo += fo
                mfc += fc
                mio += io
                mic += ic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # determine minor delta
                # current = 0.1
                print('loop_major, loop_minor', loop_major, loop_minor)
                if dc.sp.curr.major.v == 0 and dc.sp.curr.minor.v == 1:
                    if loop_major == 0:
                        Δ_minor = loop_minor
                    if loop_major > 0:
                        Δ_minor = sum(len(dc.sp.m._(s).idx.v) for s \
                                        in range(loop_major)) \
                                        + loop_minor + 1
                if dc.sp.curr.major.v == 0 and dc.sp.curr.minor.v > 1:
                    if loop_major == 0:
                        Δ_minor = loop_minor - dc.sp.curr.minor.v + 1
                    if loop_major > 0:
                        Δ_minor = sum(len(dc.sp.m._(s).idx.v) for s in range(1,
                            loop_major)) \
                            + m + len(dc.sp.m._(0).idx.v) + 2 \
                            - dc.sp.curr.minor.v
                if dc.sp.curr.major.v == 1:
                    if loop_major == 0:
                        Δ_minor = -1 * (dc.sp.curr.minor.v \
                                   + (len(dc.sp.m._(0).idx.v) - loop_minor))
                    if loop_major == dc.sp.curr.major.v:
                        Δ_minor = loop_minor - dc.sp.curr.minor.v + 1
                    if loop_major > dc.sp.curr.major.v:
                        Δ_minor = sum(len(dc.sp.m._(s).idx.v) for s in
                                range(dc.sp.curr.major.v + 1, loop_major))\
                            + loop_minor + 1 \
                            + len(dc.sp.m._(dc.sp.curr.major.v).idx.v) \
                            - dc.sp.curr.minor.v
                if dc.sp.curr.major.v > 1:
                    if loop_major < dc.sp.curr.major.v:
                        Δ_minor = -1 * ((len(dc.sp.m._(loop_major).idx.v)
                                        - loop_minor)
                            + sum(len(dc.sp.m._(s).idx.v) for s
                                in range(loop_major + 1, dc.sp.curr.major.v))
                            + dc.sp.curr.minor.v + 1)
                        if loop_major == 0:
                            Δ_minor -= 1
                    if loop_major == dc.sp.curr.major.v:
                        Δ_minor = loop_minor - dc.sp.curr.minor.v + 1
                    if loop_major > dc.sp.curr.major.v:
                        Δ_minor = sum(len(dc.sp.m._(s).idx.v) for s in
                                range(x+1,loop_major))\
                            + loop_minor + 1\
                            + len(dc.sp.m._(dc.sp.curr.major.v).idx.v) \
                            - dc.sp.curr.minor.v
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                oo = False
                if Δ_minor > 1:
                    sign = '+'
                    icon = '◇'
                    oo = True
                if Δ_minor == 1:
                    sign = '+'
                    icon = '◈'
                    oo = True
                    self.next_x = loop_major
                    self.next_y = loop_minor
                if Δ_minor == 0:
                    sign = ''
                    icon = '◆'
                if Δ_minor < 0:
                    sign = '-'
                    icon = '◆'
                if open_only and not oo:
                    continue
                Δ_majorm = '{}{},{}'.format(sign, abs(Δ_major), abs(Δ_minor))
                label = '{}   v{}.{}   {}   f:{}/{}   i:{}/{}'.format(
                    icon,loop_major,loop_minor,Δ_majorm,fc,fo+fc,ic,io+ic)
                if sel_x == loop_major and sel_y == loop_minor \
                        and open_only and Δ_minor > 0:
                    self.setText(label)
                    self.current_text = label
                elif sel_x == loop_major and sel_y == loop_minor \
                        and not open_only:
                    self.setText(label)
                    self.current_text = label
                elif Δ_minor == 1:
                    self.setText(label)
                    self.current_text = label
                action.setText(label)
                action.triggered.connect(self.onSelectionChanged)
                loop_major_menu.addAction(action)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            oo = False
            if Δ_major > 0:
                icon = '◇'
                oo = True
            if Δ_major == 0:
                icon = '◈'
                oo = True
            if Δ_major < 0:
                icon = '◆'
            if open_only and not oo:
                loop_major_menu.close()
                continue
            title = '{}   v{}.x   f:{}/{}   i:{}/{}'\
                    .format(icon, loop_major, mfc, mfo+mfc, mic, mio+mic)
            loop_major_menu.setTitle(title)
            self.root_menu.addMenu(loop_major_menu)
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

