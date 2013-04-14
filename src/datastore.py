# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import pickle, gzip, os

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxDataStore:

    """
    This class will contain all data that will be stored.  It takes care
    of saving and loading. If no path is specified yet, it will prompt
    for one, if not already present and not passed
    """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent):

        self.version   = 1
        self.app_name  = 'nelia1'
        self.extension = '.nelia1'
        self.default_path   = os.path.expanduser('~/Documents')

        # parent widget (to focus the question boxes)
        self.parent = parent
        self.path = None
        # project id 0 == project meta data (i.e. no real project)
        self.project = {0: {'next_id': 1}}
        self.run = {}
        self.reset()

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

        """
        If we already know the file path, compile and write the data. Otherwise
        prompt the user for save path.
        """

        # not reqired if no changes are made
        if not self.run['changed']:
            return

        # compile save data
        data = {
            'meta': {
                'version': self.version,
                'app_name': self.app_name
            },
            'project': self.project,
        }

        # read path, if necessary
        if not path and not self.path:

            file_name = QFileDialog.getSaveFileName(
                self.parent.w_main,
                'Save nelia1 document', self.default_path,
                'Nelia Files (*{})'.format(self.extension))[0]

            if file_name == '':
                return

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
            title = 'Save failed'
            message = 'Save failed! ' + str(e)
            QMessageBox.critical(self.parent.w_main, title, message)
            self.path = None
            return False

        # update application data state
        self.run['changed'] = False
        return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def open_document(self, path=None):

        """
        Ask the user for a file path and then load the data and reset state
        data.
        """

        # if status changed, question if user wishes to proceed
        # (discarding updates since last save)
        if self.run['changed']:
            response = QMessageBox.question(
            self.parent.w_main,
            'Discard changes?',
            'Opening a file will discard your changes. Do you want to proceed?',
            QMessageBox.Yes|QMessageBox.No)

            if response == QMessageBox.StandardButton.No:
                return

        # read path, if necessary
        if not path:

            self.path = QFileDialog.getOpenFileName(
                self.parent.w_main,
                'Open nelia1 document', self.default_path,
                'Nelia Files (*{})'.format(self.extension))[0]

            # path dialog aborted
            if not self.path:
                return False
        else:
            self.path = path

        # read data from file
        try:
            with open(self.path, 'rb') as f:
                decompressed = gzip.decompress(f.read())
            data = pickle.loads(decompressed)
        except Exception as e:
            title = 'Open failed'
            message = 'Open failed! ' + str(e)
            QMessageBox.critical(self.parent.w_main, title, message)
            self.path = None
            return False

        self.run['config'].config_data['datastore'] ['lastpath'] = self.path

        # populate data
        del self.project
        self.project = data['project']

        self.reset() # reset runtime data

        return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

