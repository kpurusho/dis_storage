import unittest
import config

class TestConfig(unittest.TestCase):
    def test_config_ctr(self):
        c = config.Config('./uploads',10,1024,1)
        self.assertEqual('./uploads', c.storageDir)
        self.assertEqual(10, c.nodeCount)
        self.assertEqual(1024, c.sizePerSlice)
        self.assertEqual(1, c.redundancyCount)


if __name__ == '__main__':
    unittest.main()