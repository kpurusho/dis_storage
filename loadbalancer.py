import config
import os
import nodetracker
import pathlib

class LoadBalancerBase:
    def __init__(self, conf:config.Config, ntracker:nodetracker.NodeTracker):
        self.Config = conf
        self.NodeTracker = ntracker

    def getPaths(self, parts:list, basepartname:str) -> dict:
        raise NotImplementedError

class RoundRobinLoadBalancer(LoadBalancerBase):
    def __init__(self, conf:config.Config, ntracker:nodetracker.NodeTracker):
        super().__init__(conf, ntracker)
    
    def getPaths(self, parts:list, basepartname:str) -> dict:
        result = {}
        nodeidx = 0
        nodeids = self.getOrderedNodeIds()
        partcount = len(parts)
        for redidx in range(1,self.Config.redundancyCount+1):
            nodeidx = self.updatePaths(nodeidx, parts, basepartname, nodeids, result)
            if (redidx*partcount) % 2 == 1:
                nodeidx = nodeidx - 1
            nodeidx = self.getNextNodeIdx(nodeidx)
        return result

    def updatePaths(self, nodeidx:int, parts:list, basepartname:str, nodeids:list, result:dict) -> int:
        for partidx in range(0,len(parts)):
            partfilename = basepartname + '_part' + str(partidx)
            partfilepath = os.path.join(self.getNodePath(nodeids[nodeidx]), partfilename)
            if str(partidx) in result:
                result[str(partidx)].append(partfilepath)
            else:
                result[str(partidx)] = [partfilepath]

            partidx = partidx + 1
            nodeidx = self.getNextNodeIdx(nodeidx)

        return nodeidx

    def getNodePath(self, nodeid:int) -> str:
        uploadpath = self.Config.storageDir
        nodeprefix = 'node_'
        return os.path.join(uploadpath, nodeprefix + str(nodeid))

    def getNextNodeIdx(self, nodeidx:int) -> int:
        return (nodeidx + 1) % self.Config.nodeCount

    def getOrderedNodeIds(self):
        node_size_id_list = []
        for nodeid in range(0, self.Config.nodeCount):
            node_size_id_list.append((self.getNodeSize(self.getNodePath(nodeid)), nodeid))
        node_size_id_list = sorted(node_size_id_list, key = lambda x: x[0])
        nodeidlist = []
        for size_id in node_size_id_list:
            nodeidlist.append(size_id[1])

        return nodeidlist

    def getNodeSize(self, nodepath:str) -> int:
        root_directory = pathlib.Path(nodepath)
        return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())