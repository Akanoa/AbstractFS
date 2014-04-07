'''
Created on 1 avr 2014

@author: yguern
'''
import unittest
import os, sys, urlparse, StringIO, random, time

CLASS_PATH = os.path.join(os.path.dirname(__file__), '..', '..','classes', 'AbstractFS')
sys.path.append(CLASS_PATH)

from Local_Fs import Local_Fs

import shutil,time

class TestLocal_Fs(unittest.TestCase):

    def test_get(self):
        '''
        we generate a file with random content then we test equality between stream content return and generate content
        '''
        l = Local_Fs()
        content=""
        filepath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file.txt"
        stream = StringIO.StringIO()

        with open("file.txt", "w") as f:
            for i in range(1000):
                n = random.randint(0,100)
                content+=str(n)
                f.write(str(n))

        #test running
        self.assertTrue(l.get(filepath, stream))

        #test retunr content
        self.assertEqual(stream.getvalue(), content)


    def test_put(self):
        '''
        we generate a file with random content then we test equality between stream content return and generate content
        '''
        l = Local_Fs()
        content=""
        srcpath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file.txt"
        dstpath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file2.txt"

        stream = StringIO.StringIO()
        l.get(srcpath, stream)

        #test running
        self.assertTrue(l.put(dstpath, stream))


        # test return content
        self.assertEqual(open(srcpath).readlines(), open(dstpath).readlines())

        #clean up
        os.remove(srcpath)
        os.remove(dstpath)

    def test_makedirs(self):
        '''
        we make tree and we test existence of it
        '''
        l = Local_Fs()
        path = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\path\\to\\file"

        #test running
        self.assertTrue(l.makedirs(path))

        #test tree existence
        self.assertTrue(os.path.isdir(path))

        #cleanup
        try:
            os.removedirs(path)
        except:
            pass

    def test_rmdirs(self):
        '''
        we destroy tree and we test non-existence of it
        '''
        l = Local_Fs()

        root="D:\SVNs\\admin\scripts\UnitTests\AbstractFs\path"
        path = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\path\\to\\file"
        try:
            os.makedirs(path)
        except:
            pass

        open(path+"\\truc", "w")

        #test running
        self.assertTrue(l.rmdirs(path))
        self.assertTrue(l.rmdirs(root, True))

        #test tree existence
        self.assertFalse(os.path.isdir(root))

    def test_delete(self):
        '''
        we destroy file and test non-existence of it
        '''
        l = Local_Fs()
        filepath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\truc"

        open(filepath, "w")

        #test running
        self.assertTrue(l.delete(filepath))

        #test file existence
        self.assertFalse(os.path.isfile(filepath))

    def test_move(self):
        '''
        we move some file and we test existence dst and non-existence of src
        '''
        l = Local_Fs()

        src = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file1"
        dst = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file2"

        content=""
        with open(src, "w") as f:
            for i in range(1000):
                n = random.randint(0,100)
                content+=str(n)
                f.write(str(n))

        #test running
        self.assertTrue(l.move(src, dst))

        #test files
        self.assertTrue(os.path.isfile(dst))
        self.assertFalse(os.path.isfile(src))

        #test file integrity
        self.assertEqual(content, open(dst).readlines()[0])

        #clean up
        os.remove(dst)

    def test_copy(self):
        '''
        we copy some file and we test existence dst and non-existence of src
        '''
        l = Local_Fs()

        src = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file1"
        dst = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file2"

        content=""
        with open(src, "w") as f:
            for i in range(1000):
                n = random.randint(0,100)
                content+=str(n)
                f.write(str(n))

        #test running
        self.assertTrue(l.copy(src, dst))

        #test file integrity
        self.assertEqual(open(src).readlines(), open(dst).readlines())

        #clean up
        os.remove(src)
        os.remove(dst)

if __name__ == "__main__":
    sys.argv.append('-vv')
    unittest.main()
