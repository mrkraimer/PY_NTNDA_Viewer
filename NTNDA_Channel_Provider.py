# NTNDA_Channel_Provider.py


class NTNDA_Channel_Provider(object) :
    '''
    Base class for monitoring an NTNDArray channel from an areaDetector IOC.
    The methods are call by NTNDA_Viewer.
    '''

    def __init__(self) :
        self.channelName = None
    def setChannelName(self,channelName) :
        self.channelName = channelName
    def getChannelName(self) :
        return self.channelName
    def start(self) :
        ''' called to start monitoring.'''
        raise Exception('derived class must implement NTNDA_Channel_Provider.start')
    def stop(self) :
        ''' called to stop monitoring.'''
        raise Exception('derived class must implement NTNDA_Channel_Provider.stop')
    def done(self) :
        ''' called when NTNDA_Viewer is done.'''
        pass
    def callback(self,arg) :
        ''' must call NTNDA_Viewer.callback(arg).'''
        raise Exception('derived class must implement NTNDA_Channel_Provider.callback')

