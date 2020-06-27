import uuid

def create_metadata(name:str, partCount:int, partpaths:dict) -> dict:
        metadata = {}
        metadata['name'] = name
        metadata['partcount'] = partCount
        metadata['partpaths'] = partpaths
        metadata['id'] = str(uuid.uuid4())
        return metadata

    

        