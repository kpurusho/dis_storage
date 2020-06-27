import json
from objectifier import Objectifier
import requests
import os


test_configs = Objectifier(json.load(open('Test/testconfig.json')))


def upload_a_file(file):
    files = {'file': open(file, 'rb')}
    rs = requests.put(url=test_configs.API_SERVER_URL+'/files', files=files , verify=False)
    return rs


def retrive_a_file_by_id(id):
    rs = requests.get(url=test_configs.API_SERVER_URL+'/files/{id}'.format(id = id), allow_redirects = True, verify=False)
    return rs


def reterive_a_file_by_name(name):
    return retrive_a_file_by_id(name)


def list_available_files():
    rs = requests.get(url=test_configs.API_SERVER_URL+'/files/list', verify=False)
    return rs


def delete_a_file_by_id(id):
    rs = requests.delete(url=test_configs.API_SERVER_URL+'/files/{id}'.format(id = id), verify=False)
    return rs


def delete_a_file_by_name(name):
    return delete_a_file_by_id(name)


def rename_folder(source_dir, new_name):
    status = None
    try:
        os.rename(source_dir, new_name)
        status = True
    except:
        status = False
    return status
    
def is_slice_in_list(s,l):
        len_s = len(s) #so we don't recompute length of s on every iteration
        return any(s == l[i:len_s+i] for i in range(len(l) - len_s+1))

def upload_result(result):
    try:
        requests.post(url = test_configs.result_url+'/addresult', json = result, verify = False)
    except:
        pass