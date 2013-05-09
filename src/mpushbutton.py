# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from datacore import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MPushButton(QPushButton):
    """
    This class contains a push button with menu that is displaying the
    milestone version and enables to select milestone (e.g. for
    current selection or for feature / issue targets).
    """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent=None, change_callback=None,
                 sel_x=None, sel_y=None, open_only=False):

        super().__init__(parent)

        x = dc.sp.curr.major.v
        y = dc.sp.curr.minor.v

        self.setText('        no data        ')
        self.root_menu = QMenu(self)
        self.setMenu(self.root_menu)
        self.change_callback = change_callback

        """
        ### DELTA CALCULATION ###
        The following nested loop is somewhat hard to digest.  (At least, it
        was quite hard to create). It calculates the major and minor deltas
        of each milestone version compared to the current version. Δn
        is the difference of major milestone, quite simple.  Δm is the
        challangeing part: it is the total difference of minor milestone
        compared to the current one. E.g. If you are at version
        3.4, version 1 and two have 5 milestone each, then the minor delta
        for 1.2 will be 2 + 5 + 4 = (-)11. Major will be -2 -> -2,11 See
        nelia/calculations/version-delta.py for detailed discussion.
        """

        # loop through major dc.spro.v['milestone']
        Δn = 0
        for n in range(len(dc.spro.v['milestone'])):
            Δn = n - x
            # major version menu instance (will be labeled further down)
            major_menu = QMenu(self)

            # loop through minor dc.spro.v['milestone']
            Δm = 0
            # reset major version feature counters
            mfo = mfc = mio = mic = 0
            for m in range(len(dc.spro.v['milestone'][n])):

                # create action instance
                action = QAction(self)

                # compute minor version feature / issue count
                fo = len(dc.spro.v['milestone'][n][m]['fo'])
                fc = len(dc.spro.v['milestone'][n][m]['fc'])
                io = len(dc.spro.v['milestone'][n][m]['io'])
                ic = len(dc.spro.v['milestone'][n][m]['ic'])

                # add to major version feature / issue count
                mfo += fo
                mfc += fc
                mio += io
                mic += ic

                # 0.x series starts with 0.1 instead of 0.0
                if n == 0:
                    m += 1

                # current version = 0.0 (no dc.spro.v['milestone'] reached)
                if x == 0 and y == 0:
                    if n == 0:
                        Δm = m
                    if n > 0:
                        Δm = sum(len(dc.spro.v['milestone'][s])
                                  for s in range(n)) + m + 1
                # current version = 0.y, y>0
                if x == 0 and y > 0:
                    if n > 0:
                        Δm = sum(len(dc.spro.v['milestone'][s])
                                  for s in range(1,n)) \
                                + m + len(dc.spro.v['milestone'][0]) - y + 1
                    else:
                        Δm = m - y
                # current version = 1.y, y>=0
                if x == 1:
                    if n == x:
                        Δm = m - y
                    if n > x:
                        Δm = sum(len(dc.spro.v['milestone'][s])
                                  for s in range(x+1,n)) \
                                + m + len(dc.spro.v['milestone'][x]) - y
                    if n < x:
                        Δm = -1 * (y + (len(dc.spro.v['milestone'][0])-m))
                        if n == 0:
                            Δm -= 1
                # current major version > 1
                if x > 1:
                    if n == x:
                        Δm = m - y
                    if n > x:
                        Δm = sum(len(dc.spro.v['milestone'][s])
                                  for s in range(x+1,n)) \
                                + m + len(dc.spro.v['milestone'][x]) - y
                    if n < x:
                        Δm = -1 * (
                            (  len(dc.spro.v['milestone'][n]) - m)
                             + sum(len(dc.spro.v['milestone'][s])
                                   for s in range(n+1, x))
                             + y  )
                        if n == 0:
                            Δm -= 1

                # compute completion symbol and sign
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

                # Compute major and minor version combined delta.
                # Notice how this has nothing to do with floating point.
                # Instead it's two deltas, major, and combined minor.
                Δnm = '{}{},{}'.format(sign, abs(Δn), abs(Δm))

                # compute minor version label,
                # set it to action and add action to major_menu
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
                action.triggered.connect(self.selectionChanged)
                major_menu.addAction(action)

            # compute major version icon
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

            # set major version menu label and add it to the root menu
            major_menu.setTitle('{}   v{}.x   f:{}/{}   i:{}/{}'.format(
                icon, n, mfc, mfo+mfc, mic, mio+mic))
            self.root_menu.addMenu(major_menu)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getVersion(self):
            """
                Retrive currently seelected version.
            """

            x, y = self.current_text.split(' ')[3][1:].split('.')
            return int(x), int(y)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def selectionChanged(self):
        """
            This callback is invoked when a milestone is selected.
        """

        old_text = self.text()
        self.current_text = self.sender().text()
        if old_text == self.current_text:
            return

        self.setText(self.current_text)

        # execute external callback, e.g. for roadmap table widget update
        if self.change_callback:
            x, y = self.getVersion()
            self.change_callback(x, y, self.current_text)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

