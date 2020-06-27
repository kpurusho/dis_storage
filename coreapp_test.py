import unittest
import coreapp
import config
import os
import shutil
import hashlib
import loadbalancer
import nodetracker
import fileop


class TestableNodeTracker(nodetracker.NodeTracker):
    def __init__(self, conf:config.Config):
        nodecount = conf.nodeCount
        self.nodeStaus = []
        while nodecount > 0:
            self.nodeStaus.append(True)
            nodecount = nodecount - 1

        super().__init__(conf)
    
    def set_node_status(self, nodeid:int, status:bool):
        self.nodeStaus[nodeid] = status

    def is_node_available(self, nodeid:int) -> bool:
        return self.nodeStaus[nodeid]
        

class CoreAppTests(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(config.Config().storageDir, ignore_errors=True)
        self.conf = config.Config(redundancyCount=1)
        self.nt = TestableNodeTracker(self.conf)
        self.fop = fileop.FileOp(self.nt)
        self.lb = loadbalancer.RoundRobinLoadBalancer(self.conf, self.nt)
        self.app = coreapp.CoreApp(self.conf, self.lb, self.fop, {})
        self.app.setup()

    def test_001_init(self):
        self.assertTrue(os.path.isdir('./uploads/node_0'))
        self.assertTrue(os.path.isdir('./uploads/node_9'))

    def test_002_upload_512(self):
        self.app.upload('./test_resource/512.bin')
        self.assertTrue(os.path.exists('./uploads/node_0/512.bin_part0'))

    def test_003_upload_1024(self):
        self.app.upload('./test_resource/1024.bin')
        self.assertTrue(os.path.exists('./uploads/node_0/1024.bin_part0'))

    def test_004_upload_5000(self):
        self.app.upload('./test_resource/5000.bin')
        self.assertTrue(os.path.exists('./uploads/node_4/5000.bin_part4'))

    def test_005_upload_12000(self):
        self.app.upload('./test_resource/12000.bin')
        self.assertTrue(os.path.exists('./uploads/node_0/12000.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_9/12000.bin_part9'))
        self.assertTrue(os.path.exists('./uploads/node_1/12000.bin_part11'))

    def test_006_load_balancer(self):
        self.app.upload('./test_resource/512.bin')
        self.app.upload('./test_resource/1024.bin')
        self.app.upload('./test_resource/5000.bin')
        self.app.upload('./test_resource/10240.bin')
        self.app.upload('./test_resource/12000.bin')
        self.assertTrue(os.path.exists('./uploads/node_0/512.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_1/1024.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_2/5000.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_6/5000.bin_part4'))
        self.assertTrue(os.path.exists('./uploads/node_7/10240.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_5/10240.bin_part9'))
        self.assertTrue(os.path.exists('./uploads/node_7/12000.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_8/12000.bin_part11'))

    def test_007_load_balancer_redundency_2(self):
        self.conf.redundancyCount = 2
        self.app.upload('./test_resource/5000.bin')
        self.app.upload('./test_resource/1024.bin')
        self.app.upload('./test_resource/512.bin')

        self.assertTrue(os.path.exists('./uploads/node_0/5000.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_4/5000.bin_part4'))
        self.assertTrue(os.path.exists('./uploads/node_5/5000.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_9/5000.bin_part4'))
        self.assertTrue(os.path.exists('./uploads/node_4/1024.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_9/1024.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_0/512.bin_part0'))
        self.assertTrue(os.path.exists('./uploads/node_1/512.bin_part0'))

    def test_008_download_12000(self):
        id = self.app.upload('./test_resource/12000.bin')
        (filename, content) = self.app.download(id)
        with open('./test_resource/12000.bin', 'rb') as f:
            source = f.read()
            self.assertEqual(hashlib.md5(source).hexdigest(), hashlib.md5(content).hexdigest())

    def test_009_download_12000_one_node_down(self):
        self.conf.redundancyCount = 2
        id = self.app.upload('./test_resource/12000.bin')
        self.nt.set_node_status(8,False)
        (filename, content) = self.app.download(id)
        self.assertFileContent('./test_resource/12000.bin', content)

    def test_010_download_random_all_but_one_node_down(self):
        self.conf.redundancyCount = 10
        id12000 = self.app.upload('./test_resource/12000.bin')
        id512 = self.app.upload('./test_resource/512.bin')
        id10240 = self.app.upload('./test_resource/10240.bin')
        id1024 = self.app.upload('./test_resource/1024.bin')
        id5000 = self.app.upload('./test_resource/5000.bin')
        self.nt.set_node_status(0,False)
        self.nt.set_node_status(1,False)
        self.nt.set_node_status(2,False)
        self.nt.set_node_status(3,False)
        self.nt.set_node_status(4,False)
        self.nt.set_node_status(5,False)
        self.nt.set_node_status(6,False)
        self.nt.set_node_status(7,False)
        self.nt.set_node_status(8,False)
        self.assertFileContent('./test_resource/12000.bin', self.app.download(id12000)[1])
        self.assertFileContent('./test_resource/512.bin', self.app.download(id512)[1])
        self.assertFileContent('./test_resource/10240.bin', self.app.download(id10240)[1])
        self.assertFileContent('./test_resource/1024.bin', self.app.download(id1024)[1])
        self.assertFileContent('./test_resource/5000.bin', self.app.download(id5000)[1])

    def test_011_delete(self):
        id = self.app.upload('./test_resource/512.bin')
        self.app.delete(id)
        self.assertFalse(os.path.exists('./uploads/node_5/512.bin_part0'))

    def test_012_getlist(self):
        self.app.upload('./test_resource/512.bin')
        self.app.upload('./test_resource/5000.bin')
        result = self.app.getlist()

        self.assertEqual(2, len(result))

    def assertFileContent(self, filename:str, result:bytes):
        with open(filename, 'rb') as f:
            source = f.read()
            self.assertEqual(hashlib.md5(source).hexdigest(), hashlib.md5(result).hexdigest())

if __name__=='__main__':
    unittest.main()