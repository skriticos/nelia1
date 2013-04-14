# ------------------------------------------------------------------------------
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# All rights reserved
# ------------------------------------------------------------------------------
import sys, os, pickle, gzip
from datastore import data

# ------------------------------------------------------------------------------
class NxConfig:

    """
    This class stores the configuration of the application. This includes the
    widget states (sorting, filters) and the last opened path.
    """

# ------------------------------------------------------------------------------
    def __init__(self):

        # configuration is stored in $HOME/.config/nelia1/nelia1.config
        self.home = os.path.expanduser('~')
        self.basepath = os.path.join(self.home, '.config', 'nelia1')
        self.fullpath = os.path.join(self.basepath, 'nelia1.config')

        os.makedirs(self.basepath, exist_ok=True)

        # general pointers to the data and widgets we need
        self.project = data.run['w_project']
        self.log     = data.run['w_log']
        self.roadmap = data.run['w_roadmap']

        # internal config data structure
        self.config_data = {
            'datastore': {},
            'project': {},
            'log': {},
            'roadmap': {}
        }

        # read config on initialisation (application startup)
        self.readConfig()

# ------------------------------------------------------------------------------
    def writeConfig(self):

        # write current application state to configuration file
        pickled_data = pickle.dumps(self.config_data, 3)
        compressed_data = gzip.compress(pickled_data)

        with open(self.fullpath, 'wb') as f:
            f.write(compressed_data)

# ------------------------------------------------------------------------------
    def readConfig(self):

        # read application configuration from config file
        if not os.path.exists(self.fullpath):
            self.no_config = True
            return

        with open(self.fullpath, 'rb') as f:
                file_buffer = f.read()

        decompressed = gzip.decompress(file_buffer)
        self.config_data = pickle.loads(decompressed)
        self.no_config = False

# ------------------------------------------------------------------------------

