# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys, time
from PySide.QtCore import *
from PySide.QtGui import *
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MilestoneControl(QObject):
    # triggered when milestone tree is changed
    milestone_tree_changed = Signal()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        super().__init__(None)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # create new, empty milestone tree for dc.sp
    def setup_new(self):
        if 'm' in dc.sp.__dict__.keys():
            del dc.sp.m
        # milestone items
        dc.sp.m.mi.nextid.v   = 1       # next new milestone id
        dc.sp.m.mi.index.v    = {}      # miid → (major, minor) index
        # milestones general
        dc.sp.m.active.v      = (0, 1)  # active milestone
        dc.sp.m.selected.v    = (0, 1)  # selected milestone
        dc.sp.m.index.v       = {0, 1}  # index of major milestones
        # v0.1
        dc.sp.m._0.index.v    = {1}     # index of minor milestones
        dc.sp.m._0._1.index.v = {}      # index miids in milestone
        dc.sp.m._0._1.info.v  = ''      # milestone description
        # v1.0
        dc.sp.m._1.index.v    = {0}     # index of minor milestones
        dc.sp.m._1._0.index.v = {}      # index miids in milestone
        dc.sp.m._1._0.info.v  = ''      # milestone description
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def add_milestone_item(self,
            major, minor,
            name, info,
            mi_type, priority, category):
        timestamp = int(time.time())
        # register new milestone item
        miid = dc.sp.m.mi.nextid.v
        dc.sp.m.mi.nextid.v += 1
        dc.sp.m._(major)._(minor).index.v.add(miid)
        dc.sp.m.mi.index.v[miid] = (major, minor)
        # set attributes
        dc.sp.mi._(miid).mi_type.v = mi_type
        dc.sp.mi._(miid).status.v = 'open'
        dc.sp.mi._(miid).name.v = name
        dc.sp.mi._(miid).info.v = info
        dc.sp.mi._(miid).priority.v = priority
        dc.sp.mi._(miid).category.v = category
        dc.sp.mi._(miid).created.v = timestamp
        dc.sp.mi._(miid).modified.v = timestamp
        return miid
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def modify_milestone_item(self,
            miid,
            major, minor,
            name, description,
            mi_type, priority, category):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def delete_milestone_item(self, miid):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def close_milestone_item(self, miid):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reopen_milestone_item(self, miid):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def move_milestone_item(self, miid, major, minor):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def update_milestone_tree(self):
        pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MilestoneButton(QPushButton):
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
                    self.current_text = labe
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
def updateMsTree():
    for major in reversed(list(dc.sp.m.idx.v)):
        major_index = dc.sp.m.idx
        loop_major = dc.sp.m._(major)
        if major > 1:
            previous_major_has_item \
                    = bool(len(dc.sp.m._(major-1)._(0).idx.v))
            if not previous_major_has_item:
                major_index.v.remove(major)
                del dc.sp.m.__dict__['_{}'.format(major)]
                continue
        if major > 0:
            next_major_exists = major+1 in major_index.v
            has_item = bool(len(loop_major._(0).idx.v))
            if has_item and not next_major_exists:
                major_index.v.add(major+1)
                next_major = dc.sp.m._(major+1)
                next_major.idx.v = {0}
                next_major._(0).description.v = ''
                next_major._(0).idx.v = set()
                loop_major.idx.v.add(1)
                loop_major._(1).description.v = ''
                loop_major._(1).idx.v = set()
                continue
        lastminor = max(loop_major.idx.v)
        last_minor_has_item = bool(len(loop_major._(lastminor).idx.v))
        if last_minor_has_item:
            loop_major.idx.v.add(lastminor+1)
            loop_major._(lastminor+1).description.v = ''
            loop_major._(lastminor+1).idx.v = set()
        if major == 0 and lastminor == 1: continue
        if lastminor == 0: continue
        has_multiple_minors = False
        if major == 0 and lastminor > 1:
            has_multiple_minors = True
        if major > 0 and lastminor > 0:
            has_multiple_minors = True
        previous_to_last_minor_has_item \
                = bool(len(loop_major._(lastminor-1).idx.v))
        if has_multiple_minors and not previous_to_last_minor_has_item:
            loop_major.idx.v.remove(lastminor)
            del loop_major.__dict__['_{}'.format(lastminor)]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

