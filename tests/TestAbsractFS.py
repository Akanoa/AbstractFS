'''
Created on 1 avr 2014

@author: yguern
'''
import unittest
import os, sys, urlparse,StringIO,shutil

CLASS_PATH = os.path.join(os.path.dirname(__file__), '..', '..','classes')
sys.path.append(CLASS_PATH)


from AbstractFS import  fs

class TestAbstractFS(unittest.TestCase):

    def test__formatUrl(self):
        '''
        decompose an url in dict, so to test we recompose url and we test equality between source url and made url
        '''
        url1 = "ftp://tartampion@10.1.8.241/path"
        url1_reformated = "ftp://tartampion@10.1.8.241:21/path"
        res = fs._formatUrl(url1)
        self.assertEqual(url1_reformated, urlparse.urlunparse((res["handler"], res["netloc"]+":21", res["path"], "", "", "")))

        url2 = "ftp://tartampion@10.1.8.241:21/path"
        url2_reformated = "ftp://tartampion@10.1.8.241:21/path"
        res = fs._formatUrl(url2)
        self.assertEqual(url2_reformated, urlparse.urlunparse((res["handler"], res["netloc"], res["path"], "", "", "")))

    def test__searchHandler(self):
        '''
        we add some handler and we want to found then following their credentials
        '''
        url1 = "ftp://tartampion@10.1.8.241:21/path2"
        handler1 = fs._getHandler(url1)

        url2 = "ftp://tartampion@10.1.8.241/path2"
        handler2 = fs._getHandler(url2)

        # # print fs._handlers["ftp"]

        url3 = "ftp://tartampion@10.1.8.241:21/path2"
        url3 = fs._formatUrl(url3)

        url4 = "ftp://tartampion@10.1.8.241/path2"
        url4 = fs._formatUrl(url4)


        self.assertEqual(fs._searchHandler(url3), handler1)
        self.assertEqual(fs._searchHandler(url4), handler2)

        url1 = "ftp://tartampion@10.1.8.241:21/path"
        url2 = "ftp://tartampion2@10.1.8.241:21/path"
        handler1 = fs._getHandler(url1)
        handler2 = fs._getHandler(url2)


        #both of then must be the same, because there are same credential
        self.assertEqual(fs._searchHandler(url3), handler1)
        #conversely for two differents credentials, it's must have two different connection so two different instances
        self.assertNotEqual(fs._searchHandler(url3), handler2)


    def test__getHandler(self):
        '''
        In case of error _getHandler return False
        '''
        #it's must be valid credentials
        file_src = "ftp://tartampion@10.1.8.241:8021"
        file_dst = "ftp://tartampion@10.1.8.241:8021"
        self.assertEqual(fs._getHandler(file_src), fs._getHandler(file_dst))

    def test_makedirs(self):
        '''
        For all protocol we create tree, then we test existence of the path
        '''

        ##########Local###############

        #tree what you want create must be correct
        local_path = "L:/yolo/path"
        
        #test correct running
        self.assertNotEqual(fs.makedirs(local_path), False)

        #test correct behavior
        #try if tree exists in fs
        res = False
        if os.path.isdir(local_path):
            res = True
        self.assertTrue(res)

        #cleanup
        shutil.rmtree(local_path)


        ########FTP###################

        #tree what you want create must be correct
        ftp_path = "ftp://tartampion@10.1.8.241/path/to/file"
        #get an ftp handler to make some test
        ftp = fs._getHandler(ftp_path)

        #test correct running
        self.assertTrue(fs.makedirs(ftp_path))

        #test correct behavior
        #try if tree exist on ftp server
        res = False
        try:
            ftp._ftp.cwd(urlparse.urlparse(ftp_path).path)
            res = True
        except Exception:
            pass

        self.assertTrue(res)



    def test_rmdirs(self):
        '''
        For all protocol we delete tree, then we test existence of the path
        '''

        ##########Local###############

        #tree what you want destroy must be correct
        local_path  = "file://L:/yolo"
        local_path2 = "L:/yolo"
        
        #test correct running
        self.assertNotEqual(fs.rmdirs(local_path), False)

        #test correct behavior
        #try if tree exists in fs
        self.assertNotEqual(os.path.isdir(local_path2), True)


        #######FTP###################

        #tree what you want destroy must be correct
        path = "/path/to/file"
        credentials = "ftp://tartampion@10.1.8.241"
        ftp_path = credentials+path
        #get an ftp handler to make some test
        ftp = fs._getHandler(ftp_path)

        #test correct running
        self.assertNotEqual(fs.rmdirs(ftp_path), False)

        #test correct behavior
        #try if tree exist on ftp server
        res = True
        try:
            ftp._ftp.cwd(urlparse.urlparse(ftp_path).path)
        except Exception:
            res = False

        self.assertFalse(res)

    def test_copy(self):
        '''
        for all protocols we copy a file the we test integrity of copy file
        '''
        ##########Local###############

        #-------------------------------------------------------------

        #!!! Local -> Local
        file_src = "file://L:/file.txt"
        file_dst = "file://L:/file.txt.cpy"

        file_src_path = "L:/file.txt"
        file_dst_path = "L:/file.txt.cpy"

        handler = fs._getHandler(file_src)

        #generation src file
        with open(file_src_path, "wb") as f:
            f.write("hsdsgnhedgknjkhdgufshedfh")

        #test running
        self.assertTrue(fs.copy(file_src, file_dst))

        #test file integrity

        self.assertEqual(("").join(open(file_src_path).readlines()), ("").join(open(file_dst_path).readlines()))

        #cleanup
        os.remove(file_src_path)  
        os.remove(file_dst_path)  

        #-------------------------------------------------------------

        #!!! FTP -> FTP

        #this file must exists
        file_src = "ftp://tartampion@10.1.8.241/file_test.txt"
        file_dst = "ftp://tartampion@10.1.8.241/file_test.txt.cpy"

        file_src_path = "/file_test.txt"
        file_dst_path = "/file_test.txt.cpy"

        handler = fs._getHandler(file_src)

        #generation src file
        stream = StringIO.StringIO()
        stream.write("ramdom content")
        handler.put(file_src_path, stream)

        #test running
        self.assertTrue(fs.copy(file_src, file_dst))

        #test file integrity
        self.content = ""
        self.content2 = ""
        def callback(s):
            self.content += s

        handler._ftp.retrbinary('RETR '+ file_src_path, callback)

        def callback(s):
            self.content2 += s

        handler._ftp.retrbinary('RETR '+ file_dst_path, callback)

        self.assertEqual(self.content, self.content2)

        #cleanup
        handler.delete(file_src_path)
        handler.delete(file_dst_path)


        #-------------------------------------------------------------

        #!!! Local -> FTP
        file_src = "file://L:/file.txt"
        file_dst = "ftp://tartampion@10.1.8.241/file_test.txt"

        file_src_path = "L:/file.txt"
        file_dst_path = "/file_test.txt"

        handler = fs._getHandler(file_dst)

        #generation src file
        with open(file_src_path, "wb") as f:
            f.write("hsdsgnhedgknjkhdgufshedfh")

        #test running
        self.assertTrue(fs.copy(file_src, file_dst))

        #test file integrity
        self.content2 = ""

        def callback(s):
            self.content2 += s

        handler._ftp.retrbinary('RETR '+ file_dst_path, callback)

        self.assertEqual(("").join(open(file_src_path).readlines()), self.content2)


        #cleanup
        os.remove(file_src_path)
        handler.delete(file_dst_path)

        #-------------------------------------------------------------

        #!!! FTP -> Local
        file_src = "ftp://tartampion@10.1.8.241/file_test.txt"
        file_dst = "file://L:/file.txt"

        file_src_path = "/file_test.txt"
        file_dst_path = "L:/file.txt"

        handler = fs._getHandler(file_src)

        #generation src file
        stream = StringIO.StringIO()
        stream.write("ramdom content")
        handler.put(file_src_path, stream)

        #test running
        self.assertTrue(fs.copy(file_src, file_dst))

        #test file integrity
        self.content2 = ""

        def callback(s):
            self.content2 += s

        handler._ftp.retrbinary('RETR '+ file_src_path, callback)

        self.assertEqual(("").join(open(file_dst_path).readlines()), self.content2)

        #cleanup
        handler.delete(file_src_path)
        os.remove(file_dst_path)


    def test_move(self):
        '''
        for all protocols we copy a file the we test integrity of copy file
        '''
        ##########Local###############

        #-------------------------------------------------------------

        #!!! Local -> Local
        file_src = "file://L:/file.txt"
        file_dst = "file://L:/file.txt.cpy"

        file_src_path = "L:/file.txt"
        file_dst_path = "L:/file.txt.cpy"

        handler = fs._getHandler(file_src)

        #generation src file
        content = "hsdsgnhedgknjkhdgufshedfh"
        with open(file_src_path, "wb") as f:
            f.write(content)

        #test running
        self.assertTrue(fs.move(file_src, file_dst))

        #test file integrity

        self.assertEqual(content, ("").join(open(file_dst_path).readlines()))

        #test deleting src file

        res = True
        try:
            open(file_src)
        except Exception:
            res = False

        self.assertFalse(res)

        #cleanup
        os.remove(file_dst_path)  

        #-------------------------------------------------------------

        #!!! FTP -> FTP

        #this file must exists
        file_src = "ftp://tartampion@10.1.8.241/file_test.txt"
        file_dst = "ftp://tartampion@10.1.8.241/file_test.txt.cpy"

        file_src_path = "/file_test.txt"
        file_dst_path = "/file_test.txt.cpy"

        handler = fs._getHandler(file_src)

        #generation src file
        stream = StringIO.StringIO()
        stream.write("ramdom content")
        handler.put(file_src_path, stream)

        #test running
        self.assertTrue(fs.move(file_src, file_dst))

        #test file integrity
        self.content2 = ""

        def callback(s):
            self.content2 += s

        handler._ftp.retrbinary('RETR '+ file_dst_path, callback)

        self.assertEqual("ramdom content", self.content2)

        #test deleting src file
        self.assertFalse(handler.delete(file_src_path))

        #cleanup
        handler.delete(file_dst_path)


        #-------------------------------------------------------------

        #!!! Local -> FTP
        file_src = "file://L:/file.txt"
        file_dst = "ftp://tartampion@10.1.8.241/file_test.txt"

        file_src_path = "L:/file.txt"
        file_dst_path = "/file_test.txt"

        handler = fs._getHandler(file_dst)

        #generation src file
        content = "hsdsgnhedgknjkhdgufshedfh"
        with open(file_src_path, "wb") as f:
            f.write(content)

        #test running
        self.assertTrue(fs.move(file_src, file_dst))

        #test file integrity
        self.content2 = ""

        def callback(s):
            self.content2 += s

        handler._ftp.retrbinary('RETR '+ file_dst_path, callback)

        self.assertEqual(content, self.content2)


        #test deleting src file
        res = True
        try:
            open(file_src)
        except Exception:
            res = False

        self.assertFalse(res)


        #cleanup
        handler.delete(file_dst_path)

        #-------------------------------------------------------------

        #!!! FTP -> Local
        file_src = "ftp://tartampion@10.1.8.241/file_test.txt"
        file_dst = "file://L:/file.txt"

        file_src_path = "/file_test.txt"
        file_dst_path = "L:/file.txt"

        handler = fs._getHandler(file_src)

        #generation src file
        stream = StringIO.StringIO()
        stream.write("ramdom content")
        handler.put(file_src_path, stream)

        #test running
        self.assertTrue(fs.move(file_src, file_dst))

        #test file integrity

        self.assertEqual("ramdom content", ("").join(open(file_dst_path).readlines()))

        #test deleting src file
        self.assertFalse(handler.delete(file_src_path))

        #cleanup
        os.remove(file_dst_path)

    def test_delete(self):
        '''
        we create then we delete it
        '''
        #!!! Local
        file_src = "file://L:/file.txt"
        file_src_path = "L:/file.txt"

        #creating file
        with open(file_src_path, "wb") as f:
            f.write("ghsdeiuhgsuidhgu")

        #test running
        self.assertTrue(fs.delete(file_src))

        #test deleting
        self.assertFalse(os.path.isfile(file_src))

        #!!! FTP
        file_src = "ftp://tartampion@10.1.8.241:8021/file.txt"
        file_src_path = "/file.txt"

        handler = fs._getHandler(file_src)

        #creating file
        stream = StringIO.StringIO()
        stream.write("ramdom content")
        handler.put(file_src_path, stream)

        #test running
        self.assertTrue(fs.delete(file_src))

        #test deleting
        self.assertFalse(handler.delete(file_src_path))


if __name__ == "__main__":
    sys.argv.append('-vv')
    unittest.main()
