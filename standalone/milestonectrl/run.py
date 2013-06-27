# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from datacore import dc, _dcdump
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

