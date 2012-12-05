#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
import pickle, gzip, os

class DataStore:

    """
        This class will contain all data that will be stored.
        It takes care of saving and loading. If no path is specified
        yet, it will prompt for one, if not already present and not
        passed
    """

    def __init__(self, parent):

        self.version = 1
        self.app_name = 'Nelia'

        self.parent = parent               # parent widget (to focus the question boxes)
        self.path = None
        self.project = {0: {'next_id': 1}} # project id 0 == project meta data (i.e. no real project)
        self.run = {}                      # Shared runtime data, not saved
        self.reset()

    def reset(self):

        del self.run
        self.run = {
            'changed':          False, # global, if anything changes (bool)
            'curr_milestone':   None,  # last completed milestone (x,y)
            'next_milestone':   None,  # next milestone     (x,y)
            'sel_milestone':    None   # selected milestone (m,n)
        }

    def save(self, path=None):
        
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
                'Save projects',
                os.path.expanduser('~/Documents'),
                'Nelia Files (*.nelia)')[0]

            if file_name.rfind('.nelia') != len(file_name) - 6:
                file_name += '.nelia'

            self.path = file_name

        # compress and save data
        pickled_data = pickle.dumps(data, 3)
        compressed_data = gzip.compress(pickled_data)

        with open(self.path, 'wb') as f:
            f.write(compressed_data)

        # update application data state
        self.run['changed'] = False


    def load(self, path=None):

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
        if not path and not self.path:

            self.path = QFileDialog.getOpenFileName(
                self.parent.w_main,
                'Open projects',
                os.path.expanduser('~/Documents'),
                'Nelia Files (*.nelia)')[0]

            # path dialog aborted
            if not self.path:
                return False

        # read data from file
        with open(self.path, 'rb') as f:
                file_buffer = f.read()

        decompressed = gzip.decompress(file_buffer)
        data = pickle.loads(decompressed)

        # populate data
        del self.project
        self.project = data['project']

        self.reset() # reset runtime data

        return True

# vim: set ts=4 sw=4 ai si expandtab:

