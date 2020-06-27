import unittest
import fileop

class FileOpTests(unittest.TestCase):
    def test_file_split_size_512(self):
        chunks = fileop.split('./test_resource/512.bin', 1024)
        self.assertEqual(1, len(chunks))
        self.assertEqual(512, len(chunks[0]))

    def test_file_split_size_1024(self):
        chunks = fileop.split('./test_resource/1024.bin', 1024)
        self.assertEqual(1, len(chunks))
        self.assertEqual(1024, len(chunks[0]))

    def test_file_split_size_5000(self):
        chunks = fileop.split('./test_resource/5000.bin', 1024)
        self.assertEqual(5, len(chunks))
        self.assertEqual(1024, len(chunks[0]))
        self.assertEqual(904, len(chunks[4]))

    def test_file_split_size_10240(self):
        chunks = fileop.split('./test_resource/10240.bin', 1024)
        self.assertEqual(10, len(chunks))
        self.assertEqual(1024, len(chunks[0]))
        self.assertEqual(1024, len(chunks[9]))

    def test_file_split_size_12000(self):
        chunks = fileop.split('./test_resource/12000.bin', 1024)
        self.assertEqual(12, len(chunks))
        self.assertEqual(1024, len(chunks[0]))
        self.assertEqual(736, len(chunks[11]))

    def test_file_join_size_512(self):
        chunks = fileop.split('./test_resource/512.bin', 1024)
        fullfile = fileop.join(chunks)
        self.assertEqual(512, len(fullfile))

    def test_file_join_size_1024(self):
        chunks = fileop.split('./test_resource/1024.bin', 1024)
        fullfile = fileop.join(chunks)
        self.assertEqual(1024, len(fullfile))

    def test_file_join_size_5000(self):
        chunks = fileop.split('./test_resource/5000.bin', 1024)
        fullfile = fileop.join(chunks)
        self.assertEqual(5000, len(fullfile))

    def test_file_join_size_10240(self):
        chunks = fileop.split('./test_resource/10240.bin', 1024)
        fullfile = fileop.join(chunks)
        self.assertEqual(10240, len(fullfile))

    def test_file_join_size_12000(self):
        chunks = fileop.split('./test_resource/12000.bin', 1024)
        fullfile = fileop.join(chunks)
        self.assertEqual(12000, len(fullfile))

if __name__=='__main__':
    unittest.main()
