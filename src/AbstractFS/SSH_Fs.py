from Base_Fs import Base_Fs

class SSH_Fs(Base_Fs):
    def __init__(self):
        Base_Fs.__init__(self)

    def setCredentials(self, hostname, port, username, password):
        '''
        classdoc
        '''
        print hostname
        
    def getNetloc(self):
        '''
        classdoc
        '''
        user, passwd, host, port = self._credentials
        netloc = ""
        if user !=None:
            netloc += user
        elif user!=None and passwd!=None:
            netloc += user+":"+passwd

        netloc += "@"+host+":"+port