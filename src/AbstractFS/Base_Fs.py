class Base_Fs:
    '''
    abstract class all method must be redefined in subclass
    handle primitives action on FS
    '''
    def __init__(self):
        '''
        abstract class all method must be redefined in subclass
        '''
        pass

    def setCredentials(self, hostname, port, username, password):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method setCredentials is not yet implemented in subclass!")

    def getNetloc(self):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method getNetloc is not yet implemented in subclass!")

    def makedirs(self, tree):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method makedirs is not yet implemented in subclass!")

    def rmdirs(self, tree):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method rmdirs is not yet implemented in subclass!")
        
    def put(self, path):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method put is not yet implemented in subclass!")

    def get(self, path):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method get is not yet implemented in subclass!")

    def delete(self, path):
        '''
        abstract method, must be redefined in inheritance classes
        '''
        raise NotImplementedError("Method put is not yet implemented in subclass!")