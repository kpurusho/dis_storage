import pytest
import transactions as txn
from objectifier import Objectifier
import json
from filehash import FileHash
from uuid import uuid4
import csv
from datetime import datetime
import os
import socket

config = Objectifier(json.load(open('Test/testconfig.json')))

class TestMilestone1():

    def setup_method(self):
        self.test_suite_name = os.environ['test_selector']
        self.status = 'Fail'
        self.status = 'Fail'
        md5= FileHash('sha1')
        self.chksum = md5.hash_file('Test/Milestone1Tests.py')
        self.active_test=os.environ['ACTIVE_TEST']

    #envsetup
    def test_one(self):
        """
            Delete all the files on the server
        """
        self.test_name = self.test_one.__doc__        
        try:
            files = txn.list_available_files().json()
            for items in files:
                rs = txn.delete_a_file_by_id(items['id'])
                assert(rs.status_code==200)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e
    # Verify that when there are no files, the list call displays no results
    def test_two(self):
        """
        Verify that the list Files returns no files when there are no files to be displayed
        """
        self.test_name = self.test_two.__doc__        
        try:
            response = txn.list_available_files().json()
            assert(response.__len__()==0)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e    

    # Verify that a file can be uploaded successfully 
    def test_three(self):
        """
        Verify that the a file can be uploaded successfully
        """
        self.test_name = self.test_three.__doc__        
        try:
            response = txn.upload_a_file(config.TEST_DATA.test_three.file_to_upload)
            assert(response.status_code==200)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that the uploaded file can be reterived sucessfully - Verify check sum
    def test_four(self):
        """
        Verify that the uploaded file can be reterived sucessfully - Verify check sum before upload and after reterive
        """
        self.test_name = self.test_four.__doc__        
        try:
            md5= FileHash('sha1')
            hash = md5.hash_file(config.TEST_DATA.test_four.file_to_upload)
            response = txn.upload_a_file(config.TEST_DATA.test_four.file_to_upload)
            assert(response.status_code==200)
            id = response.text
            r = txn.retrive_a_file_by_id(id)       
            open(config.TEST_DATA.test_four.file_name, 'wb+').write(r.content)
            hash_2 = md5.hash_file(config.TEST_DATA.test_four.file_name)
            assert(hash==hash_2)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that when there are files , the list call displays the files correctly 
    def test_five(self):
        """
        Verify that when there are files , the list call displays the files correctly 
        """
        self.test_name = self.test_five.__doc__        
        try:
            count = txn.list_available_files().json()
            assert(count.__len__()>0)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that a delete operation happens successfully
    def test_six(self):
        """
        Verify that a delete operation happens successfully
        """
        self.test_name = self.test_six.__doc__        
        try:
            response = txn.upload_a_file(config.TEST_DATA.test_five.file_to_upload)
            assert(response.status_code==200)
            id = response.text
            r = txn.retrive_a_file_by_id(id)  
            assert(r.status_code==200)
            delete= txn.delete_a_file_by_id(id)
            assert(delete.status_code==200)
            r = txn.retrive_a_file_by_id(id)
            assert(r.status_code==404)
            list_of_files = txn.list_available_files().json()
            assert(str(id) not in str(list_of_files))
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e    


    # Verify that appopriate error message is displayed while trying to access a file that doesnt exist
    def test_seven(self):
        """
        Verify that appopriate error message is displayed while trying to access a file that doesnt exist
        """
        self.test_name = self.test_seven.__doc__        
        try:
            r = txn.retrive_a_file_by_id(str(uuid4()))  
            assert(r.status_code==404)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    
    # Verify that an error is returned while trying to upload a duplicate file
    def test_ten(self):
        """
            Verify that an error is returned while trying to upload a duplicate file
        """
        self.test_name = self.test_ten.__doc__        
        try:
            response = txn.upload_a_file(config.TEST_DATA.test_ten.file_to_upload)
            assert(response.status_code==200)
            response = txn.upload_a_file(config.TEST_DATA.test_ten.file_to_upload)
            assert(response.status_code==409)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

        # Verify that files of various names are accepted during upload
    def test_eleven(self):
        """
        Verify that files of various names are accepted during upload
        """
        self.test_name = self.test_eleven.__doc__        
        try:
            file_names = list(config.TEST_DATA.test_eleven.file_names)
            for items in file_names:
                open("Test/TestData/"+items,'w+')
                upload_stat = txn.upload_a_file("Test/TestData/"+items)
                assert(upload_stat.status_code==200)
            list_of_files = txn.list_available_files().json()
            
            file_names_Actual=[]
            for files in list_of_files:
                file_names_Actual.append(files['file_name'])
            assert(txn.is_slice_in_list(file_names,file_names_Actual) , True)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that appropriate error is retured while trying to delete a file that is not present
    def test_twelve(self):
        """
        Verify that 404 is returned while trying to delete a file that does not exist
        """
        self.test_name = self.test_twelve.__doc__        
        try:
            response = txn.upload_a_file(config.TEST_DATA.test_twelve.file_to_upload)
            assert(response.status_code==200)
            id = response.text
            response = txn.delete_a_file_by_id(id)
            assert(response.status_code==200)
            response = txn.delete_a_file_by_id(id)
            assert(response.status_code==404)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def teardown_method(self):
        result = {'rollNumber': os.environ.get('ROLL_NUM'), 'testSuite': self.test_suite_name,
                  'testCase': self.test_name.replace('\n', '').strip()+self.active_test,
                  'status': self.status, 'ranAt': str(datetime.now()), 'hostName': socket.gethostname(),'checksum':self.chksum , 'metaData':"",'testID':str(config.testID)}
        with open(r'Results/ResultStore.csv', 'a') as csvfile:
            fieldnames = ['rollNumber', 'testSuite',
                          'testCase', 'status', 'ranAt', 'hostName', 'checksum','metaData','testID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(result)
        txn.upload_result(result)