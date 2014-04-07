# -*- coding:utf-8 -*-
from Local_Fs import Local_Fs
from FTP_Fs   import FTP_Fs
from SSH_Fs   import SSH_Fs

import sys, urlparse, StringIO

class Abstract_FsException(Exception):
    """
    Handle ftplib Exception
    """
    def __init__(self, err, method=""):
        self.err = err
        self.method = method
    def __str__(self):
        try:
            err = self.err.get_error()
            return "AbstractFsException in method '"+self.method+"': "+err.lstrip(" ")
        except AttributeError:
            return "AbstractFsException: "+str(self.err)

class AbstractFS:
    '''
    This is an abstraction class to handle file system through various protocols like ftp, ssh or localFs
    @note: don't try to instantiate this class use like this following example:

    >>> from AbstractFs import fs
    >>> fs.move("src", "dest")
    '''

    id = 0
    '''
    number of instance
    @note: if id=1 this class no more be instantiated
    '''

    def __init__(self):
        '''
        constructor of Abstract Fs
        '''
        if self.__class__.id:
            raise Exception("This class can't be instanciate")
            return
            
        self._handlers = {"file":[Local_Fs, ""], "ftp":[FTP_Fs, 21], "ssh":[SSH_Fs, 22]}
        self.__class__.id+=1


    def _formatUrl(self, url):
        '''
        transforms an URL in dict
        @param url: following U{RCF-1738<http://www.ietf.org/rfc/rfc1738.txt>}
        @return: url hashes with this pattern:
            - handler 
            - username
            - password
            - hostname
            - port
            - path 
            - netloc
        @rtype: L{dict}
        '''
        try:
            if len(url.split('://'))<2:
                url = "file://"+url

            parsed = urlparse.urlparse(url)
            scheme, netloc, path = parsed[0:3]

            ###Handle windows letter drive
            if scheme == "file" and netloc != " ":
                path = netloc+"/"+path
                netloc = ""
                port = None
            else:
                if parsed.port == None:
                    port = self._handlers[scheme][1]
                else:
                    port = parsed.port

            #get credentials coming from netloc

            return {"handler":scheme, 
                    "username":parsed.username, 
                    "password":parsed.password,
                    "hostname":parsed.hostname,
                    "port":port,
                    "path":path,
                    "netloc":netloc
                    }
        except Exception, e:
            raise Abstract_FsException("Invalid protocol, for the moment only ["+(" ,").join(sorted(self._handlers.keys()))+"], are availables")

    def _searchHandler(self, url):
        '''
        searches an handler in his list
        @param url: following U{RCF-1738<http://www.ietf.org/rfc/rfc1738.txt>}
        @returns:
        if handler found L{Base_Fs}

        otherwise L{None}
        ''' 

        try:
            list_handler = self._handlers[url["handler"]]
            
            ##The local file
            if url["handler"] == "file":
                if len(list_handler)==2:
                    return None
                elif len(list_handler)==3:
                    return list_handler[2]

            url_str = urlparse.urlunparse((url["handler"],url["netloc"],"" , "","" ,""))

            netloc = url["handler"]+"://"
            if url["username"]:
                netloc += url["username"]
            if url["password"]:
                netloc += ":"+url["password"]
            if url["username"]:
                netloc += "@"
            netloc += url["hostname"]+":"+str(url["port"])

            
            for handler in self._handlers[url["handler"]][2:]:
                url_handler = handler.getNetloc()
                if url_handler == netloc:
                    return handler
                    
            return None
        except Exception, e:
            raise Abstract_FsException(e)
            return False
            

    def _getHandler(self, url):
        '''
        get an handler to do fs actions
        @returns:
        if credentials doesn't correspond to existing class handler, returns L{False}

        otherwise L{Base_Fs}
        '''
        try:
            url_parsed = self._formatUrl(url)

            if not url_parsed["handler"] in self._handlers.keys():
                raise Abstract_FsException("Invalid protocol, for the moment only ["+(" ,").join(sorted(self._handlers.keys()))+"], are availables")


            handler_found = self._searchHandler(url_parsed)

            if  handler_found != None:
                return handler_found

            list_handler = self._handlers[url_parsed["handler"]]

            #instanciation of a new handler for connection
            handler_instance = list_handler[0]()

            #adding credentials
            if url_parsed["netloc"]!="":
                url_parsed.__delitem__("netloc")
                url_parsed.__delitem__("path")
                url_parsed.__delitem__("handler")
                if not handler_instance.setCredentials(**url_parsed):
                    print "please verify your credentials"
                    return False

            list_handler.append(handler_instance)

            return handler_instance
        except Exception, e:
            raise Abstract_FsException(e)
            return False
        

    #############################################
    #            called methods                 #
    #############################################

    def copy(self, src, dst):
        '''
        copies a file
        @warning: all path must write like this: B{[handler://user:pass@host:]path}
        @note: if only path is declared, it's wille be an local copy
        @param src: file you want copy
        @param dst: destination of copy file 
        @return: result of copy
        @rtype: bool

        @raise Exception: something went wrong during the copy
        '''
        handler_src = self._getHandler(src)
        handler_dst = self._getHandler(dst)

        if not handler_src or not handler_dst:
            raise Exception

        src = self._formatUrl(src)
        dst = self._formatUrl(dst)

        try:
            if src["handler"] == "file" and dst["handler"] == "file":
                handler_src.copy(src["path"], dst["path"])

            elif src["handler"] !="file" or dst["handler"] != "file" :
                stream = StringIO.StringIO()
                handler_src.get(src["path"], stream)
                handler_dst.put(dst["path"], stream)
        except Exception, e:
            raise Abstract_FsException(e, "copy")
            return False
        return True

    def delete(self, path):
        '''
        deletes a file
        if only path is declared the copy will be local
        @param path: path to the file you want to delete formatted as [handler://user:pass@host:]path

        @return: result of delete
        @rtype: bool

        @raise Exception: something went wrong during the deleting
        '''
        handler = self._getHandler(path)
        path = self._formatUrl(path)["path"]
        try:
            handler.delete(path)
        except Exception, e:
            raise Abstract_FsException(e, "delete")
            return False
        return True

    def move(self, src, dst):
        '''
        moves a file
        if only path is declared the copy will be local
        @param src: file whose you want make a copy formatted as [handler://user:pass@host:]path
        @param dst: destination of copy file formatted as [handler://user:pass@host:]path

        @return: result of move
        @rtype: bool

        @raise Exception: something went wrong during the move

        '''
        handler_src = self._getHandler(src)
        handler_dst = self._getHandler(dst)

        if not handler_src or not handler_dst:
            raise Exception("This protocol is not yet implemented, for moment only: "+" ,".join(self._handlers.keys()))

        src = self._formatUrl(src)
        dst = self._formatUrl(dst)

        try:
            if src["handler"] == "file" and dst["handler"] == "file":
                handler_src.move(src["path"], dst["path"])

            elif src["handler"] !="file" or dst["handler"] != "file" :
                stream = StringIO.StringIO()
                handler_src.get(src["path"], stream)
                handler_dst.put(dst["path"], stream)
                handler_src.delete(src["path"])
        except Exception, e:
            raise Abstract_FsException(e, "move")
            return False
        return True

    def makedirs(self, tree):
        '''
        makes recursively foldera
        if folder already exists, passes to son folder
        @param tree: tree what you want create formatted as [handler://user:pass@host:]path

        @return: result of mkdirs
        @rtype: bool

        @raise Exception: something went wrong during creation of tree
        '''
        handler = self._getHandler(tree)
        tree = self._formatUrl(tree)["path"]
        try:
            handler.makedirs(tree)
        except Exception, e:
            raise Abstract_FsException(e, "makedirs")
        return True

    def rmdirs(self, tree, delete_file=True):
        '''
        remove recursively folder
        if folder isn't empty and delete_file=False removes files into folder before
        otherwise raise exception
        @param tree: tree what you want create formatted as [handler://user:pass@host:]path
        @param delete_file: allows to delete files into folders before to delete folders

        @return: result of rmdirs
        @rtype: bool

        @raise Exception: something went wrong during destruction of tree
        '''
        handler = self._getHandler(tree)
        tree = self._formatUrl(tree)["path"]
        try:
            handler.rmdirs(tree)
        except Exception, e:
            raise Abstract_FsException(e, "rmdirs")
            return False
        return True

fs = AbstractFS()#: @warning: singleton of AbstractFS  do not try to instantiate it