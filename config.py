import sys, os, pickle, gzip

class NxConfig:

    def __init__(self, data):

        self.home = os.path.expanduser('~')
        self.basepath = os.path.join(self.home, '.config', 'nelia1')
        self.fullpath = os.path.join(self.basepath, 'nelia1.config')

        os.makedirs(self.basepath, exist_ok=True)

        self.data    = data
        self.project = self.data.run['w_project']
        self.log     = self.data.run['w_log']
        self.roadmap = self.data.run['w_roadmap']

        self.config_data = {
            'datastore': {},
            'project': {},
            'log': {},
            'roadmap': {}
        }

        self.readConfig()

    def writeConfig(self):

        pickled_data = pickle.dumps(self.config_data, 3)
        compressed_data = gzip.compress(pickled_data)

        with open(self.fullpath, 'wb') as f:
            f.write(compressed_data)

    def readConfig(self):

        if not os.path.exists(self.fullpath):
            self.no_config = True
            return

        with open(self.fullpath, 'rb') as f:
                file_buffer = f.read()

        decompressed = gzip.decompress(file_buffer)
        self.config_data = pickle.loads(decompressed)
        self.no_config = False
        return

