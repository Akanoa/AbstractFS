from Base_Fs import Base_Fs
import ftplib
from ftplib import FTP


import os


class FTP_FsExecption(Exception):
    """
    Handle ftplib Exception
    """
    def __init__(self, err):
        self.err = err
    def get_error(self):
        return self.err.args[0][3:]
    def __str__(self):
        return "Error FTPFs"




class FTP_Fs(Base_Fs):
    '''
    Handle primitive action on FTP FS
    '''
    def __init__(self):
        Base_Fs.__init__(self)
        self._ftp = None
        self._credentials = None

    def setCredentials(self, hostname, port, username, password):
        '''
        try to connect to FTP server
        @param hostname:
        @param port:
        @param username:
        @param password:
        @type hostname: str
        @type port : int
        @type username : str
        @type password : str
        @return: success or fail
        @rtype: bool
        '''
        OK=False
        if not port:
            port = 21

        self._credentials = (hostname, port, username, password)

        try:
            self._ftp = FTP()
            self._ftp.connect(hostname, port)
            if   username != None and password != None:
                self._ftp.login(username, password)
            elif username != None and password == None:
                self._ftp.login(username)
            else:
                self._ftp.login()
            OK=True
        except ftplib.error_reply as e:
            raise FTP_FsExecption(e)
        finally:
            return OK

    def makedirs(self,tree):
        '''
        makes tree on local FS
        @param tree: absolute path
        @type tree: str
        @return: success or fail
        @rtype: L{bool}
        '''
        OK=False
        try:
            if isinstance(tree, str):
                tree = tree.split("/")

            dir = tree.pop(0)
            try:
                self._ftp.mkd(dir)
            except Exception:
                pass

            if len(tree):
                tree[0]=dir+"/"+tree[0]
                self.makedirs(tree)
            OK=True
        except ftplib.error_perm as e:
            raise FTP_FsExecption(e)
            return False
        finally:
            return OK

    def rmdirs(self, root_tree, delete_file=False):
        '''
        destroy tree on local FS
        @param root_tree: absolute path of root tree you want to destroy
        @param delete_file: delete files in directory before delete it
        @type root_tree: str
        @return: success or fail
        @rtype: bool
        '''
        OK=False
        try:
            if isinstance(root_tree, str):
                root_tree = root_tree.split("/")

            root_tree_str = "/".join(root_tree) 
            
            self._ftp.cwd(root_tree_str)


            #remove files in directory
            if delete_file:
                try:
                    files = self._ftp.nlst()
                    for f in files:
                        self._ftp.delete(f)
                except Exception:
                    pass
            try:
                self._ftp.cwd("/")
                self._ftp.rmd(root_tree_str)
            except Exception, e:
                return e

            if len(root_tree):
                root_tree.pop()
                self.rmdirs(root_tree, delete_file)
            OK=True
        except ftplib.error_perm as e:
            raise FTP_FsExecption(e)
        finally:
            return OK

    def put(self, filepath, stream):
        '''
        create file from stream content at desired path
        @param filepath: absolute destination path
        @param stream: reference to stream which contents information stream
        @type filepath: str
        @type stream: U{StringIO.StringIO<https://docs.python.org/2/library/stringio.html>}
        @return: success or fail
        @rtype: bool
        '''
        OK=False
        try:
            path = os.path.dirname(filepath)
            filename = os.path.basename(filepath)

            self._ftp.cwd(path)
            stream.seek(0)
            self._ftp.storbinary("STOR "+filename, stream)
            OK=True
        except ftplib.error_perm as e:
            raise FTP_FsExecption(e)
        finally:
            return OK

    def get(self, filepath, stream):
        '''
        get file content by chunk to avoid massive memory conssumption
        @param filepath: absolute path
        @param stream: reference to stream which will gets content file
        @type filepath: str
        @type stream: U{StringIO.StringIO<https://docs.python.org/2/library/stringio.html>}
        @return: success or fail
        @rtype: bool
        '''
        OK=False
        try:
            path = os.path.dirname(filepath)
            filename = os.path.basename(filepath)

            self._ftp.cwd(path)

            def callback(s):
                stream.write(s)

            self._ftp.retrbinary("RETR "+filename, callback)
            OK=True

        except ftplib.error_perm as e:
            raise FTP_FsExecption(e)
        finally:
            return OK

    def delete(self, filepath):
        '''
        delete file on FTP server
        @param filepath: absolute path
        @return: success or fail
        @rtype: bool
        '''
        OK=False
        try:
            path = os.path.dirname(filepath)
            filename = os.path.basename(filepath)

            self._ftp.cwd(path)
            self._ftp.delete(filename)
            OK=True
        except ftplib.error_perm as e:
            raise FTP_FsExecption(e)
        finally:
            return OK

    def getNetloc(self, credentials=None):
        '''
        classdoc
        '''
        OK=False
        try:
            #unittest
            if credentials!=None:
                self._credentials = credentials

            host, port, user, passwd = self._credentials
            # print "passwd", passwd
            netloc = "ftp://"
            if user !=None and passwd==None:
                netloc += user
            elif user!=None and passwd!=None:
                netloc += user+":"+passwd

            if netloc != "ftp://":
                netloc += "@"
            netloc += host+":"+str(port)
            OK=True
            return netloc
        except Exception, e:
            raise Exception(e)
        finally:
            if not OK:
                return OK


