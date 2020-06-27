import config
import os

class NodeTracker:
    def __init__(self, conf:config.Config):
        self.Config = conf

    def is_node_available(self, nodeid:int) -> bool:
        uploadpath = self.Config.storageDir
        nodeprefix = 'node_'
        nodepath = os.path.join(uploadpath, nodeprefix + str(nodeid))
        return os.path.exists(nodepath)