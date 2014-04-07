'''
Created on 2 avr 2014

@author: yguern
'''
import unittest
import os, sys, urlparse, StringIO, random

CLASS_PATH = os.path.join(os.path.dirname(__file__), '..', '..','classes', 'AbstractFS')
sys.path.append(CLASS_PATH)

from FTP_Fs import FTP_Fs
from Local_Fs import Local_Fs

class TestFtp_Fs(unittest.TestCase):

    credentials = ("10.1.8.241", "21", "tartampion", "")

    def test_setCredentials(self):
        '''
        your credentials must be correct
        '''
        f = FTP_Fs()
        self.assertTrue(f.setCredentials(*self.credentials))


    def test_put(self):
        '''
        we generate a file with random content then we test equality between stream content return and generate content
        '''
        f = FTP_Fs()
        f.setCredentials(*self.credentials)
        l = Local_Fs()

        content=""
        self.content2=""
        srcpath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file.txt"
        dstpath = "/file_test.txt"
        stream = StringIO.StringIO()

        with open(srcpath, "w") as f1:
            for i in range(1000):
                n = random.randint(0,100)
                content+=str(n)
                f1.write(str(n))

        l.get(srcpath, stream)

        #test running
        self.assertTrue(f.put(dstpath, stream))

        def callback(s):
            self.content2 += s

        f._ftp.retrbinary('RETR '+ dstpath, callback)

        #test put content
        self.assertEqual(self.content2.rstrip('\n'), content)

        #clean up 
        os.remove(srcpath)

    def test_get(self):
        '''
        we generate a file with random content then we test equality between stream content return and generate content
        '''
        f = FTP_Fs()
        f.setCredentials(*self.credentials)

        self.content2=""
        srcpath = "/file_test.txt"

        stream = StringIO.StringIO()

        #test running
        self.assertTrue(f.get(srcpath, stream))

        def callback(s):
            self.content2 += s

        f._ftp.retrbinary('RETR '+ srcpath, callback)

        #test put content
        self.assertEqual(self.content2.rstrip('\n'), stream.getvalue())

    def test_makedirs(self):
        '''
        we create tree on FTP serv then existence of it
        '''
        f = FTP_Fs()
        f.setCredentials(*self.credentials)

        tree = "/path/to/file"

        #running test
        self.assertTrue(f.makedirs(tree))

        #test tree existence on serv
        res = False
        try:
            f._ftp.cwd(tree)
            res = True
        except Exception:
            pass

        self.assertTrue(res)

    def test_rmdirs(self):
        '''
        we create tree on FTP serv then we test existence of it
        '''
        f = FTP_Fs()
        f.setCredentials(*self.credentials)

        root = '/path'
        tree = "/path/to/file"

        #running test
        self.assertTrue(f.rmdirs(tree))

        #test tree existence on serv
        res = False
        try:
            f._ftp.cwd(root)
            res = True
        except Exception:
            pass

        self.assertFalse(res)

    def test_delete(self):
        '''
        we create file on FTP serv then we test existence of it
        '''
        f = FTP_Fs()
        l = Local_Fs()
        stream = StringIO.StringIO()
        srcpath = "D:\SVNs\\admin\scripts\UnitTests\AbstractFs\\file2.txt"
        dstpath = "file.txt"

        f.setCredentials(*self.credentials)

        with open(srcpath, "w") as f1:
            f1.write("df")

        l.get(srcpath, stream)
        f.put(dstpath, stream)

        os.remove(srcpath)

        #running test
        self.assertTrue(f.delete(dstpath))

        #test non-existence of file on server
        self.assertFalse(f.get(dstpath, stream))

    def test_getNetloc(self):
        '''
        send a dict and retrieve an url without path
        '''
        f = FTP_Fs()
        creds = [
            ("host", "21", "user", None),
            ("host", "21", "user", "pass"),
            ("host", "21", None, None),
        ]

        urls = [
            "ftp://user@host:21",
            "ftp://user:pass@host:21",
            "ftp://host:21",
        ]

        tests = [(creds[i], urls[i]) for i in range(len(creds))]
        for test in tests:
            self.assertTrue(f.getNetloc(test[0]) == test[1])

if __name__ == "__main__":
    sys.argv.append('-vv')
    unittest.main()