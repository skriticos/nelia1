# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtGui import *
import pickle, gzip, os, PySide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# data.w_*  -- widgets
# data.c_{main,project,log,roadmap,config}  -- modules
# data.getPid(), data.touchProject()  -- shorthands for the eqv. project meth.
# data.getProject()  -- get selected project instance
# data.getMilestoneItem(), data.getMilestone()  -- shorthands for roadmap
# data.run{}  -- general runtime data
# data.project{}  -- document data / storage
# data.project[0][next_id]
# data.project[pid]['log']['lid'][{created, summary, detail}]
# data.project[pid][{name, category, status, ptype, priority, challange,
#                     description, created, modified}]
# data.project[pid]['meta'][{next_log, next_roadmap_item, curr_milestone}]
# data.project[pid]['mi_index'][miid]
# data.project[pid]['milestone'][{description, m}]
# data.project[pid]['milestone'][major][minor][{fo, fc,io, ic}]
# data.project[pid]['milestone'][major][minor][fioc][miid][{
#      name,icat,priority,description,created}]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxDataStore:
    def __init__(self):
        # static variables
        self.version        = 1
        self.app_name       = 'nelia1'
        self.extension      = '.nelia1'
        self.default_path   = os.path.expanduser('~/Documents')
        # pointers
        self.initData()
        # the run path is not reset during normal open
        self.run['path']    = None
        # used to reset state on init and after loading a document
        self.reset()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def initData(self):
        self.project = {0: {'next_pid': 1}}
        self.run = {}
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reset(self):
        self.run['changed']          = False
        self.run['curr_milestone']   = None
        self.run['next_milestone']   = None
        self.run['sel_milestone']    = None
        self.run['log_pid_last']     = 0
        self.run['roadmap_pid_last'] = 0
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def save_document(self, path):
        self.run['path'] = path
        # compile save data
        data = {'meta'   : {'version': self.version, 'app_name': self.app_name},
                'project': self.project }
        # compress and save data
        try:
            pickled_data = pickle.dumps(data, 3)
            compressed_data = gzip.compress(pickled_data)
            self.conf['datastore']['lastpath'] = path
            with open(path, 'wb') as f:
                f.write(compressed_data)
        except Exception as e:
            self.run['path'] = None
            return e
        # update application data state
        self.run['changed'] = False
        return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def open_document(self, path):
        self.run['path'] = path
        # load document data to datastore
        try:
            with open(path, 'rb') as f:
                decompressed = gzip.decompress(f.read())
            data = pickle.loads(decompressed)
        # open failed, pass exception
        except Exception as e:
            self.run['path'] = None
            return e
        # save path in configuration (for NxProject.onOpenLast)
        self.conf['datastore']['lastpath'] = path
        # replace document data
        del self.project
        self.project = data['project']
        # reset runtime data
        self.reset()
        return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def convert(self, item):
        # we can't pickle PySide objects :(
        if item == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
            return PySide.QtCore.Qt.SortOrder.DescendingOrder
        if item == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
            return PySide.QtCore.Qt.SortOrder.AscendingOrder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
data = NxDataStore()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

