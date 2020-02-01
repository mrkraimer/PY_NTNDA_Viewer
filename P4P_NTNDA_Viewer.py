#!/usr/bin/env python

from NTNDA_Viewer import NTNDA_Viewer_Provider
from NTNDA_Viewer import NTNDA_Viewer

import sys,time,signal

import numpy as np
from p4p.client.thread import Context
from threading import Event
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

class P4PProvider(NTNDA_Viewer_Provider) :
    def __init__(self):
        NTNDA_Viewer_Provider.__init__(self)
        self.ctxt = Context('pva')
        self.firstCallback = True
    def start(self) :
        self.firstCallback = True
        self.subscription = self.ctxt.monitor(
              self.getChannelName(),
              self.mycallback,
              request='field(value,dimension,codec,compressedSize,uncompressedSize)',
              notify_disconnect=True)
    def stop(self) :
        self.ctxt.close()
    def done(self) :
        pass
    def mycallback(self,struct) :
        if self.firstCallback :
            arg = dict()
            arg["status"] = "connected"
            self.callback(arg)
        arg = dict()
        try :
            argtype = str(type(struct))
            if argtype.find('Disconnected')>=0 :
                arg["status"] = "disconnected"
                self.callback(arg)
                return
            arg['value'] = struct['value']
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
    p4pProvider = P4PProvider()
    viewer = NTNDA_Viewer(p4pProvider,"P4P")
    channelName = None
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
    p4pProvider.setChannelName(channelName)
    sys.exit(app.exec_())

