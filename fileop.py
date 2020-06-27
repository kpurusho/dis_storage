import io
import config
import os
import nodetracker

class FileOp:
    def __init__(self, nt:nodetracker.NodeTracker):
        self.nt = nt

    def splitcontent(self, filestream, chunkSize:int) -> list:
        result = []
        while True:
            chunk = filestream.read(chunkSize)
            if not chunk:
                break
            result.append(chunk)
        return result


    def split(self, filepath:str, chunkSize:int) -> list:
        result = []
        with open(filepath, 'rb', buffering=0)  as f:
            while True:
                chunk = f.read(chunkSize)
                if not chunk:
                    break
                result.append(chunk)
        return result

    def joinfiles(self, filepaths:list) -> bytes:
        result = bytes()
        for filepath in filepaths:
            result = result + self.readfile(filepath)
        return result

    def join(self, chunks:list) -> bytes:
        result = bytes()
        for chunk in chunks:
            result = result + chunk
        return result

    def deleteFiles(self, filepaths:list) -> None:
        for filepath in filepaths:
            os.remove(filepath)

    def writefile(self, part:bytes, partpath:str):
        with open(partpath, 'wb') as f:
            f.write(part)

    def readfile(self, partpath:str) -> bytes:
        with open(partpath, 'rb') as f:
            return f.read()

    def getFirstAvailableFilePath(self, paths:list) -> str:
        for path in paths:
            if self.nt.is_node_available(self.getNodeId(path)):
                return path
        raise Exception('No paths found!!')

    def getNodeId(self, partpath:str) -> int:
        partpath = partpath.replace('\\','/')
        folders = partpath.split('/')
        for folder in folders:
            if folder.startswith('node_'):
                return int(folder[5:])
        raise Exception('Invalid part path!!')
