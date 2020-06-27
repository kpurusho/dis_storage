class Config:
    def __init__(self, storageDir:str='./uploads', nodeCount:int=10, sizePerSlice:int=1024, redundancyCount:int=1):
        self.storageDir = storageDir
        self.nodeCount = nodeCount
        self.sizePerSlice = sizePerSlice
        self.redundancyCount = redundancyCount