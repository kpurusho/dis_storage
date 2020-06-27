import pytest
import transactions as txn
from objectifier import Objectifier
import json
import os
import shutil
from filehash import FileHash
import csv
from datetime import datetime
import os
import socket


config = Objectifier(json.load(open('Test/testconfig.json')))

class TestMilestone3():

    def setup_method(self):
        self.test_suite_name = os.environ['test_selector']
        self.status = 'Fail'
        self.status = 'Fail'
        md5= FileHash('sha1')
        self.chksum = md5.hash_file('Test/Milestone3Test.py')


    def test_one(self):
        """
            Delete all the files on the server_M3
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
    
    def test_two(self):
        """
        Verify Load Balancing
        - Have a known configuration of node count and chunk size
        - Load a sequence of files with specific sizes
        - Check the file count and distribution of load
        """
        self.test_name = self.test_two.__doc__        
        try:
            app_config = json.load(open(config.TEST_DATA.milestone_3.app_config_location))
            node_count = app_config['node_count']
            size_per_slice = app_config['size_per_slice']
            redunduncy_count = app_config['redundancy_count']
            print("\nVerifying Pre-Requisites for the Test")
            assert(node_count==4)
            assert(size_per_slice==1024)
            assert(redunduncy_count==1)
            print("\nSuccessfully verified Pre-Requisites for the test")

            #Load 10KB file 
            rs = txn.upload_a_file(config.TEST_DATA.milestone_3.file_1_path)
            assert(rs.status_code == 200)
            nodes = []
            for items in os.listdir(config.TEST_DATA.milestone_3.location_of_nodes):
                if( os.path.isdir(config.TEST_DATA.milestone_3.location_of_nodes+'/'+items) and 'node_' in items):
                    nodes.append(items)
            file_count_data = {}

            for node in nodes:
                file_count_in_that_node = 0
                file_count_in_that_node =os.listdir( os.path.join(config.TEST_DATA.milestone_3.location_of_nodes , node) ).__len__()
                file_count_data[node]= file_count_in_that_node
            
            # there must not be more than 2 files per node for the given configuration
            for key in file_count_data.keys():
                assert(file_count_data[key] <= config.TEST_DATA.milestone_3.test_2_count_1)
            
            #Load 2KB file Twice
            rs = txn.upload_a_file(config.TEST_DATA.milestone_3.file_2_path)
            assert(rs.status_code == 200)
            rs = txn.upload_a_file(config.TEST_DATA.milestone_3.file_3_path)
            assert(rs.status_code == 200)
            nodes = []
            for items in os.listdir(config.TEST_DATA.milestone_3.location_of_nodes):
                if( os.path.isdir(config.TEST_DATA.milestone_3.location_of_nodes+'/'+items) and 'node_' in items):
                    nodes.append(items)
            file_count_data = {}

            for node in nodes:
                file_count_in_that_node = 0
                file_count_in_that_node =os.listdir( os.path.join(config.TEST_DATA.milestone_3.location_of_nodes , node) ).__len__()
                file_count_data[node]= file_count_in_that_node
            
            # there must not be more than 2 files per node for the given configuration
            for key in file_count_data.keys():
                assert(file_count_data[key] <= config.TEST_DATA.milestone_3.test_2_count_2)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e
    
    def test_two_xnd(self):
        """
        Verify that chunking is done appropriately
        """
        self.test_name = self.test_two_xnd.__doc__ 
        try:
            nodes = []
            for items in os.listdir(config.TEST_DATA.milestone_3.location_of_nodes):
                if( os.path.isdir(config.TEST_DATA.milestone_3.location_of_nodes+'/'+items) and 'node_' in items):
                    nodes.append(items)
            assert(nodes.__len__()>0)
            for node in nodes:
                print(node)
                for dirpath, dirnames, filenames in os.walk(config.TEST_DATA.milestone_3.location_of_nodes+'/'+node):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)                                                                    
                        assert(os.path.getsize(fp)<=1024)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e


    def test_three(self):
        """
            Delete all the files on the server_M34
        """
        self.test_name = self.test_three.__doc__        
        try:
            files = txn.list_available_files().json()
            for items in files:
                rs = txn.delete_a_file_by_id(items['id'])
                assert(rs.status_code==200)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def test_four(self):
        """
        Verify redundancy 
        - Have a known configuration of node count , chunk size  and redunduncy level
        - Load a sequence of files with specific sizes
        - Delete number of nodes as redunduncy specification
        - Check if the files can be retrived
        """
        self.test_name = self.test_four.__doc__        
        try:
            app_config = json.load(open(config.TEST_DATA.milestone_3.app_config_location))
            node_count = app_config['node_count']
            size_per_slice = app_config['size_per_slice']
            redunduncy_count = app_config['redundancy_count']
            print("\nVerifying Pre-Requisites for the Test")
            assert(node_count==4)
            assert(size_per_slice==1024)
            assert(redunduncy_count==1)
            print("\nSuccessfully verified Pre-Requisites for the test")

            #Load 10KB file 
            md5= FileHash('sha1')
            input_checksum = md5.hash_file(config.TEST_DATA.milestone_3.file_1_path)
            rs = txn.upload_a_file(config.TEST_DATA.milestone_3.file_1_path)
            assert(rs.status_code == 200)
            file_id = str(rs.text)
            nodes = []
            for items in os.listdir(config.TEST_DATA.milestone_3.location_of_nodes):
                if( os.path.isdir(config.TEST_DATA.milestone_3.location_of_nodes+'/'+items) and 'node_' in items):
                    nodes.append(items)
            
            # delete a node
            #shutil.rmtree( os.path.join( config.TEST_DATA.milestone_3.location_of_nodes , nodes[0]) )
            #rename a file 
            os.rename(os.path.join( config.TEST_DATA.milestone_3.location_of_nodes , nodes[0]) , os.path.join( config.TEST_DATA.milestone_3.location_of_nodes , 'XYZQBC'))

            # try getting the file back 
            rs = txn.retrive_a_file_by_id(file_id)
            assert(rs.status_code==200)
            open('Output.file', 'wb+').write(rs.content)
            output_checksum = md5.hash_file('Output.file')
            assert input_checksum , output_checksum
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