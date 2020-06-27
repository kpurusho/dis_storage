import pytest
import transactions as txn
from objectifier import Objectifier
import json
import csv
from datetime import datetime
import os
import socket
from filehash import FileHash

config = Objectifier(json.load(open('Test/testconfig.json')))


class TestSanityCases():
    def setup_method(self):
        self.test_suite_name = os.environ['test_selector']
        self.status = 'Fail'
        md5= FileHash('sha1')
        self.chksum = md5.hash_file('Test/SanityTest.py')
        
        
    def test_Upload(self):
        """
        Verify that Upload of a file works fine
        """
        self.test_name = self.test_Upload.__doc__
        try:
            upload_response = txn.upload_a_file(
                config.TEST_DATA.sanity_test.file_to_upload)
            # , "status code 200 was expected , recieved {0}".format(upload_response.status_code))
            assert(upload_response.status_code in [200, 201])
            os.environ['sanity_file_name'] = upload_response.text
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def test_list(self):
        """
        Verify that list operation of files works fine
        """
        self.test_name = self.test_list.__doc__
        try:
            list_response = txn.list_available_files()
            # , "The uploaded file was not listed on the /upload/list route")
            assert(config.TEST_DATA.sanity_test.file_name in list_response.text)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def test_download(self):
        """
        Verify that Download of a file works fine
        """
        self.test_name = self.test_download.__doc__
        try:
            download_response = txn.retrive_a_file_by_id(os.environ['sanity_file_name'])
            # , "status code 200 was required during downlod, but got {0}".format(download_response.status_code))
            assert(download_response.status_code == 200)
            self.status = 'Pass'
        except Exception as e:
            self.status = 'Fail'
            raise e

    def test_delete(self):
        """
        Verify that delete operation works fine
        """
        self.test_name = self.test_delete.__doc__
        try:
            delete_response = txn.delete_a_file_by_id(os.environ['sanity_file_name'])
            # , "delete operation must return status code 200, but recieved {0}".format(delete_response.status_code))
            assert(delete_response.status_code == 200)
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
