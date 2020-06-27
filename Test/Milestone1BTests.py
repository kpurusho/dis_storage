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
        self.chksum = md5.hash_file('Test/Milestone1BTests.py')
        location_of_config = config.TEST_DATA.milestone_1b.app_config_location
        server_side_conf = json.load(open(location_of_config))
        self.servers = server_side_conf['peers']
        if(self.servers.__len__()!=set(self.servers).__len__()):
            assert 1==0, """The configured Peers in your config are not unique.
             Each entry of the configured peer must be unique
             {0}
            """.format(self.servers)
            raise """The configured Peers in your config are not unique.
             Each entry of the configured peer must be unique
             {0}
            """.format(self.servers)


    #envsetup
    def test_one(self):
        """
            Delete all the files on the server_M1B_1
        """
        self.test_name = self.test_one.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[0]
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
        Verify that  when all files are deleted from one server, the changes are reflected on other servers
        """
        self.test_name = self.test_two.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[1]
            response = txn.list_available_files().json()
            assert(response.__len__()==0)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e    



    # Verify that the uploaded file can be reterived sucessfully - Verify check sum
    def test_four(self):
        """
        Verify that a file uploaded to a server can be retrieved from another server with integrity
        """
        self.test_name = self.test_four.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[1]
            md5= FileHash('sha1')
            hash = md5.hash_file(config.TEST_DATA.milestone_1b.file_to_upload_1)
            response = txn.upload_a_file(config.TEST_DATA.milestone_1b.file_to_upload_1)
            assert(response.status_code==200)
            id = response.text
            txn.test_configs.API_SERVER_URL = self.servers[0]
            r = txn.retrive_a_file_by_id(id)       
            open(config.TEST_DATA.milestone_1b.file_name_1, 'wb+').write(r.content)
            hash_2 = md5.hash_file(config.TEST_DATA.milestone_1b.file_name_1)
            assert(hash==hash_2)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that when there are files , the list call displays the files correctly 
    def test_five(self):
        """
        Verify that when there are files uploaded to one server, the data is listed on the other server
        """
        self.test_name = self.test_five.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[1]
            count = txn.list_available_files().json()
            assert(count.__len__()>0)
            assert(config.TEST_DATA.milestone_1b.file_name_1 in str(count))
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    # Verify that a delete operation happens successfully
    def test_six(self):
        """
        Verify that a file uploaded to one server can be Deleted from another server
        """
        self.test_name = self.test_six.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[0]
            response = txn.upload_a_file(config.TEST_DATA.milestone_1b.file_to_upload_2)
            assert(response.status_code==200)
            id = response.text
            r = txn.retrive_a_file_by_id(id)  
            assert(r.status_code==200)
            txn.test_configs.API_SERVER_URL = self.servers[1]
            delete= txn.delete_a_file_by_id(id)
            assert(delete.status_code==200)
            txn.test_configs.API_SERVER_URL = self.servers[0]
            r = txn.retrive_a_file_by_id(id)
            assert(r.status_code==404)
            txn.test_configs.API_SERVER_URL = self.servers[2]
            list_of_files = txn.list_available_files().json()
            assert(str(id) not in str(list_of_files))
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e    



    
    # Verify that an error is returned while trying to upload a duplicate file
    def test_ten(self):
        """
            Verify that an error is returned while trying to upload a duplicate file on different servers
        """
        self.test_name = self.test_ten.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[0]
            response = txn.upload_a_file(config.TEST_DATA.milestone_1b.file__to_upload_3)
            assert(response.status_code==200)
            txn.test_configs.API_SERVER_URL = self.servers[1]
            response = txn.upload_a_file(config.TEST_DATA.milestone_1b.file__to_upload_3)
            assert(response.status_code==409)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e


    # Verify that appropriate error is retured while trying to delete a file that is not present
    def test_twelve(self):
        """
        Verify that 404 is returned when deleting a file that was already deleted on another server
        """
        self.test_name = self.test_twelve.__doc__        
        try:
            txn.test_configs.API_SERVER_URL = self.servers[1]
            response = txn.upload_a_file(config.TEST_DATA.milestone_1b.file_to_upload_4)
            assert(response.status_code==200)
            id = response.text
            response = txn.delete_a_file_by_id(id)
            assert(response.status_code==200)
            txn.test_configs.API_SERVER_URL = self.servers[0]
            response = txn.delete_a_file_by_id(id)
            assert(response.status_code==404)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def teardown_method(self):
        result = {'rollNumber': os.environ.get('ROLL_NUM'), 'testSuite': self.test_suite_name,
                  'testCase': self.test_name.replace('\n', '').strip(),
                  'status': self.status, 'ranAt': str(datetime.now()), 'hostName': socket.gethostname(),'checksum':self.chksum , 'metaData':"",'testID':str(config.testID)}
        with open(r'Results/ResultStore.csv', 'a') as csvfile:
            fieldnames = ['rollNumber', 'testSuite',
                          'testCase', 'status', 'ranAt', 'hostName', 'checksum','metaData','testID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(result)
        txn.upload_result(result)