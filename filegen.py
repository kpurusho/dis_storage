import io

def genfile(filepath:str, size:int):
    bytecontent = bytes([1])
    with open(filepath, 'wb') as f:
        while size > 0:
            f.write(bytecontent)
            size=size-1
