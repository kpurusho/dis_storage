import fileop
import config
import os
import loadbalancer
import filemetadata

class FileAlreadyUploadedException(Exception):
    pass

class FileNotAvailableException(Exception):
    pass

class CoreApp:
    def __init__(self, conf:config.Config, lb:loadbalancer.LoadBalancerBase, fop:fileop.FileOp, metadatastore:dict={}):
        self.Config = conf
        self.metadataStore = metadatastore
        self.lb = lb
        self.fop = fop
        
    def setup(self):
        for i in range(0,self.Config.nodeCount):
            nodedir = self.Config.storageDir + '/' + 'node_' + str(i)
            try:
                os.makedirs(nodedir, True)
            except FileExistsError:
                pass
    
    def upload_content(self, filename:str, filestream):
        for fileid in self.metadataStore:
            print(self.metadataStore[fileid]['name'])
            if filename == self.metadataStore[fileid]['name']:
                raise FileAlreadyUploadedException()

        parts = self.fop.splitcontent(filestream, self.Config.sizePerSlice)
        partpaths = self.lb.getPaths(parts, filename)
        for partkey in partpaths:
            paths = partpaths[partkey]
            for p in paths:
                self.fop.writefile(parts[int(partkey)], p)
        
        metadata = filemetadata.create_metadata(filename, len(parts),  partpaths)
        self.metadataStore[metadata['id']] = metadata
        return str(metadata['id']) 


    def upload(self, filepath:str):
        filename = os.path.basename(filepath)
        if filename in self.metadataStore:
            raise FileAlreadyUploadedException()

        parts = self.fop.split(filepath, self.Config.sizePerSlice)
        partpaths = self.lb.getPaths(parts, filename)
        for partkey in partpaths:
            paths = partpaths[partkey]
            for p in paths:
                self.fop.writefile(parts[int(partkey)], p)
        
        metadata = filemetadata.create_metadata(filename, len(parts),  partpaths)
        self.metadataStore[str(metadata['id'])] = metadata
        return str(metadata['id']) 

    def download(self, fileid:str) -> bytes:
        if fileid not in self.metadataStore:
            raise FileNotAvailableException()

        metadata = self.metadataStore[fileid]
        partfilepaths = []
        for partidx in range(0,metadata['partcount']):
            partfilepaths.append(self.fop.getFirstAvailableFilePath(metadata['partpaths'][str(partidx)]))

        return metadata['name'], self.fop.joinfiles(partfilepaths)

    def delete(self, fileid:str):
        if fileid not in self.metadataStore:
            raise FileNotAvailableException()

        metadata = self.metadataStore[fileid]
        partfilepaths = []
        for partidx in range(0,metadata['partcount']):
            print(metadata['partpaths'][str(partidx)])
            for path in metadata['partpaths'][str(partidx)]:
                partfilepaths.append(path)

        self.fop.deleteFiles(partfilepaths)
        del self.metadataStore[fileid]

    def getlist(self) -> list:
        result = []
        for filename in self.metadataStore:
            metadata = self.metadataStore[filename]
            result.append({'file_name' : metadata['name'], 'id' :  str(metadata['id'])}) 
        
        return result
