from Base_Fs import Base_Fs
import os, sys, shutil, StringIO, traceback


class Local_FsExecption(Exception):
    """
    Handle ftplib Exception
    """
    def __init__(self, err):
        self.err = err
    def get_error(self):
        return self.err.args[1]+" => "+self.err.filename
    def __str__(self):
        return "Error LocalFs: "+repr(self.err)


class Local_Fs(Base_Fs):
    '''
    Handle primitive action on local FS
    '''
    def __init__(self):
        '''
        constructor
        '''
        Base_Fs.__init__(self)

    def makedirs(self,tree):
        '''
        makes tree on local FS
        @param tree: absolute path
        @type tree: str
        @return: success or failed
        @rtype: L{bool}
        '''
        try:
            if not os.path.isdir(tree):
                os.makedirs(tree)
        except Exception, e:
            raise Local_FsExecption(e)
        return True

    def rmdirs(self,root_tree, delete_file=False):
        '''
        destroy tree on local FS
        @param root_tree: absolute path of root tree you want to destroy
        @param delete_file: delete files in directory before delete it
        @type root_tree: str
        @return: success or failed
        @rtype: bool
        '''
        OK = False
        try:
            if os.path.isdir(root_tree):
                for e in os.listdir(root_tree):
                    new_path = root_tree+"/"+e
                    if os.path.isdir(new_path):
                        self.rmdirs(new_path, delete_file)
                        os.rmdir(new_path)
                    elif os.path.isfile(new_path) and delete_file:
                        os.remove(new_path)

                if not len(os.listdir(root_tree)): 
                    os.rmdir(root_tree)
            OK = True

        except Exception, e:
            raise Local_FsExecption(e)
        finally:
            return OK

    def copy(self, src, dst):
        '''
        copy src to dst on local FS
        @param src: absolute path
        @param dst: absolute path
        @type src: str
        @type dst: str
        @return: success or failed
        @rtype: bool
        '''
        try:
            shutil.copy(src, dst)
        except Exception:
            return False
        return True

    def move(self, src, dst):
        '''
        move src to dst on local FS
        @param src: absolute path
        @param dst: absolute path
        @type src: str
        @type dst: str
        @return: success or failed
        @rtype: bool
        '''
        try:
            shutil.move(src, dst)
        except Exception, e:
            raise Local_FsExecption(e)
        return True

    def delete(self, filepath):
        '''
        deletes a file on local FS
        @param filepath: absolute path
        @type filepath: str
        @return: success or failed
        @rtype: bool
        '''
        try:
            os.remove(filepath)
        except Exception, e:
            raise Local_FsExecption(e)
        return True

    def get(self, filepath, stream):
        '''
        get file content by chunk to avoid massive memory conssumption
        @param filepath: absolute path
        @param stream: reference to stream which will gets content file
        @type filepath: str
        @type stream: U{StringIO.StringIO<https://docs.python.org/2/library/stringio.html>}
        @return: success or failed
        @rtype: bool
        '''
        try:
            shutil.copyfileobj(open(filepath), stream)
        except Exception, e:
            raise Local_FsExecption(e)
        return True

    def put(self, filepath, stream):
        '''
        create file from stream content at desired path
        @param filepath: absolute destination path
        @param stream: reference to stream which contents information stream
        @type filepath: str
        @type stream: U{StringIO.StringIO<https://docs.python.org/2/library/stringio.html>}
        @return: success or failed
        @rtype: bool
        '''
        try:
            with open(filepath, "wb") as f:
                f.write(stream.getvalue())
        except Exception, e:
            raise Local_FsExecption(e)
        return True
