# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtGui import *
import pickle, gzip, os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxDataStore:
    def __init__(self, parent):
        # static variables
        self.version        = 1
        self.app_name       = 'nelia1'
        self.extension      = '.nelia1'
        self.default_path   = os.path.expanduser('~/Documents')
        # dynamic variables
        self.path = None
        # pointers
        self.parent         = parent
        self.initData()
        self.reset()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def initData(self):
        self.project = {0: {'next_id': 1}}
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
    def save_document(self, path=None):
        if not self.run['changed']: return
        # compile save data
        data = {'meta'   : {'version': self.version, 'app_name': self.app_name},
                'project': self.project }
        # read path, if necessary
        if not path and not self.path:
            file_name = QFileDialog.getSaveFileName(
                self.parent.w_main,
                'Save nelia1 document', self.default_path,
                'Nelia Files (*{})'.format(self.extension))[0]
            # dialog aborted?
            if file_name == '': return
            extension_start = len(file_name) - len(self.extension)
            if file_name.rfind(self.extension) != extension_start:
                file_name += self.extension
            self.path = file_name
        # compress and save data
        try:
            pickled_data = pickle.dumps(data, 3)
            compressed_data = gzip.compress(pickled_data)
            self.run['config'].config_data['datastore'] ['lastpath'] = self.path
            with open(self.path, 'wb') as f:
                f.write(compressed_data)
        except Exception as e:
            title, message = 'Save failed', 'Save failed! ' + str(e)
            QMessageBox.critical(self.parent.w_main, title, message)
            self.path = None
            return False
        # update application data state
        self.run['changed'] = False
        return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def open_document(self, path=None):
        if self.run['changed']:
            response = QMessageBox.question(
                self.parent.w_main,
                'Discard changes?',
                'Opening a file will discard your changes. ' + \
                'Do you want to proceed?',
                QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.StandardButton.No: return
        # read path, if necessary
        if not path:
            self.path = QFileDialog.getOpenFileName(
                self.parent.w_main,
                'Open nelia1 document', self.default_path,
                'Nelia Files (*{})'.format(self.extension))[0]
            # path dialog aborted
            if not self.path: return False
        else: self.path = path
        # read data from file
        try:
            with open(self.path, 'rb') as f:
                decompressed = gzip.decompress(f.read())
            data = pickle.loads(decompressed)
        except Exception as e:
            title, message = 'Open failed', 'Open failed! ' + str(e)
            QMessageBox.critical(self.parent.w_main, title, message)
            self.path = None
            return False
        self.run['config'].config_data['datastore'] ['lastpath'] = self.path
        # populate data
        del self.project
        self.project = data['project']
        self.reset()
        return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

