#!/usr/bin/env python

from NTNDA_Viewer import NTNDA_Viewer_Provider
from NTNDA_Viewer import NTNDA_Viewer

import sys,time,signal

import numpy as np
from pvaccess import *
from threading import Event
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

class GetChannel(object) :
    '''
       This exists because whenever a new channel was started a crask occured
    '''
    def __init__(self, parent=None):
        self.save = dict()
    def get(self,channelName) :
        channel = self.save.get(channelName)
        if channel!=None : return channel
        channel = Channel(channelName)
        self.save.update({channelName : channel})
        return channel

class PVAPYProvider(NTNDA_Viewer_Provider) :
    def __init__(self):
        NTNDA_Viewer_Provider.__init__(self)
        self.getChannel = GetChannel()
    def start(self) :
        self.channel = self.getChannel.get(self.getChannelName())
        self.channel.monitor(self.mycallback,
              'field(value,dimension,codec,compressedSize,uncompressedSize)')
    def stop(self) :
        self.channel.stopMonitor()
    def done(self) :
        pass
    def mycallback(self,struct) :
        arg = dict()
        try :
            val = struct['value'][0]
            if len(val) != 1 :
                raise Exception('value length not 1')
            element = None
            for x in val :
                element = x
            if element == None : 
                raise Exception('value is not numpyarray')
            value = val[element]
            arg['value'] = value
            arg['dimension'] = struct['dimension']
            arg['codec'] = struct['codec']
            arg['compressedSize'] = struct['compressedSize']
            arg['uncompressedSize'] = struct['uncompressedSize']
            self.callback(arg)
            return
        except Exception as error:
            arg["exception"] = repr(error)
            self.callback(arg)
            return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    PVAPYProvider = PVAPYProvider()
    viewer = NTNDA_Viewer(PVAPYProvider,"PVAPY")
    channelName = None
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
    PVAPYProvider.setChannelName(channelName)
    sys.exit(app.exec_())

