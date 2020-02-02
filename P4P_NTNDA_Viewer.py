#!/usr/bin/env python

from NTNDA_Viewer import NTNDA_Viewer_Provider,NTNDA_Viewer
from p4p.client.thread import Context
import sys
from threading import Event
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject,pyqtSignal

class P4PProvider(QObject,NTNDA_Viewer_Provider) :
    callbacksignal = pyqtSignal()
    def __init__(self):
        QObject.__init__(self)
        NTNDA_Viewer_Provider.__init__(self)
        self.callbacksignal.connect(self.mycallback)
        self.callbackDoneEvent = Event()
        self.firstCallback = True
        
    def start(self) :
        self.ctxt = Context('pva')
        self.firstCallback = True
        self.subscription = self.ctxt.monitor(
              self.getChannelName(),
              self.p4pcallback,
              request='field(value,dimension,codec,compressedSize,uncompressedSize)',
              notify_disconnect=True)
    def stop(self) :
        self.ctxt.close()
    def done(self) :
        pass
    def p4pcallback(self,arg) :
        self.struct = arg;
        self.callbacksignal.emit()
        self.callbackDoneEvent.wait()
        self.callbackDoneEvent.clear()
    def mycallback(self) :
        struct = self.struct
        arg = dict()
        try :
            argtype = str(type(struct))
            if argtype.find('Disconnected')>=0 :
                arg["status"] = "disconnected"
                self.callback(arg)
                self.firstCallback = True
                self.callbackDoneEvent.set()
                return
            if self.firstCallback :
                arg = dict()
                arg["status"] = "connected"
                self.callback(arg)
                self.firstCallback = False
                self.callback(arg)
            arg = dict()
            arg['value'] = struct['value']
            arg['dimension'] = struct['dimension']
            arg['codec'] = struct['codec']
            arg['compressedSize'] = struct['compressedSize']
            arg['uncompressedSize'] = struct['uncompressedSize']
            self.callback(arg)
            self.callbackDoneEvent.set()
            return
        except Exception as error:
            arg["exception"] = repr(error)
            self.callback(arg)
            self.callbackDoneEvent.set()
            return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    p4pProvider = P4PProvider()
    channelName = None
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
    p4pProvider.setChannelName(channelName)
    viewer = NTNDA_Viewer(p4pProvider,"P4P")
    sys.exit(app.exec_())

