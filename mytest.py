import requests
import os


def upload_a_file(file):
    files = {'file': open(file, 'rb')}
    rs = requests.put(url='http://127.0.0.1:5000/files', files=files , verify=False)
    return rs.content

print(upload_a_file("E:\\NonProject\\official\\UniversityEngagement\\Feb-2020-Surathkal\\Student_handout_NIT\\Student_Handouts_NIT_SURATHKAL\\Validator_Windows_V3\\Test\\TestData\\test_file_1.txt"))