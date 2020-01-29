#!/usr/bin/env python

import sys,time
import numpy as np
from p4p.client.thread import Context
import threading
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from pyqtgraph.widgets.RawImageWidget import RawImageWidget
from PyQt5.Qt import QObject,Qt, Q_ARG, Q_RETURN_ARG, pyqtSlot

from PyQt5.QtCore import pyqtSignal

import ctypes
import ctypes.util
import os
from ast import literal_eval as make_tuple

class ImageDisplay(RawImageWidget,QObject):
    def __init__(self,name= 'ImageDisplay', parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent,scaled=True)
        QObject.__init__(self)
        self.setObjectName('ImageDisplay')
        self.setWindowTitle('ImageDisplay')
        self.left = 1
        self.top = 250
        self.maxsize = 800
        self.width = self.maxsize
        self.height = self.maxsize
        self.ignoreClose = True
        self.pixelLevels = (0,0)
        self.okToClose = False
        self.isHidden = True

    def closeEvent(self, event) :
        if self.ignoreClose :
            event.ignore()
            self.isHidden = True
            self.hide()

    def setPixelLevels(self,pixelLevels) :
        try :
           self.pixelLevels = make_tuple(pixelLevels)
        except Exception as error:
           self.viewer.statusText.setText("setPixelLevels error=" + repr(error))

#    @pyqtSlot(dict, result=int)
    def newImage(self,arg):
        image = arg[0]
        width = arg[1]
        height = arg[2]
        if self.isHidden or width!= self.width or height!=self.height :
            self.width = width
            self.height = height
            self.isHidden = False
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.show()
        self.setImage(image,levels=self.pixelLevels)
        return 0

class FindLibrary(object) :
    def __init__(self, parent=None):
        self.save = dict()
    def find(self,name) :
        lib = self.save.get(name)
        if lib!=None : return lib
        result = ctypes.util.find_library(name)
        if result==None : return None
        if os.name == 'nt':
            lib = ctypes.windll.LoadLibrary(result)
        else :
            lib = ctypes.cdll.LoadLibrary(result)
        if lib!=None : self.save.update({name : lib})
        return lib

class PY_NTNDA_Viewer(QWidget) :
    callbacksignal = pyqtSignal()
    def __init__(self,channelName, parent=None):
        super(QWidget, self).__init__(parent)
        self.channelName = channelName
        self.channelNameLabel = QLabel("channelName:")
        self.event = threading.Event()
        self.event.set()
        self.callbackDoneEvent = threading.Event()
        self.callbackDoneEvent.clear()
        self.setWindowTitle("PY_NTNDA_Viewer")
        self.findLibrary = FindLibrary()
# first row
        self.startButton = QPushButton('start')
        self.startButton.setEnabled(True)
        self.stopButton = QPushButton('stop')
        self.stopButton.setEnabled(False)
        self.channelNameText = QLineEdit()
        self.channelNameText.setEnabled(True)
        
        self.ctxt = Context('pva')
        self.subscription = None
        self.isStarted = False
# second row
        self.nxText = QLabel()
        self.nxText.setFixedWidth(50)
        self.nyText = QLabel()
        self.nyText.setFixedWidth(50)
        self.nzText = QLabel()
        self.nzText.setFixedWidth(20)
        self.dtypeText = QLabel()
        self.dtypeText.setFixedWidth(50)
        self.codecNameText = QLabel()
        self.codecNameText.setFixedWidth(40)
        self.compressRatioText = QLabel()
        self.compressRatioText.setFixedWidth(40)
        self.imageRateText = QLabel()
        self.imageRateText.setFixedWidth(40)
        self.pixelLevelsText = QLineEdit()
        self.pixelLevelsText.setEnabled(False)
# third row
        self.clearButton = QPushButton('clear')
        self.clearButton.setEnabled(True)
        self.statusText = QLineEdit()
# initialize
        self.lasttime = time.time() -2
        self.nImages = 0
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.datatype = None
        self.maxsize = 800
        self.minsize = 16
        self.width = self.maxsize
        self.height = self.maxsize
        self.codecName = ''
        self.compressRatio = round(1.0)
        self.compressRatioText.setText(str(self.compressRatio))
        self.initUI()

    def closeEvent(self, event) :
        if self.isStarted : 
            self.statusText.setText('PY_NTNDA_Viewer can only be closed when stopped')
            event.ignore()
            return
        if self.imageDisplay!=None :
            self.imageDisplay.okToClose = True
            self.imageDisplay.close()
        
    def startEvent(self) :
        self.start()

    def stopEvent(self) :
        self.stop()

    def clearEvent(self) :
        self.statusText.setText('')
    
    def channelNameEvent(self) :
        self.event.wait()
        try:
            self.channelName = self.channelNameText.text()
        except Exception as error:
            self.statusText.setText(repr(error))
        self.event.set()

    def pixelLevelsEvent(self) :
        self.event.wait()
        try:
            self.imageDisplay.setPixelLevels(self.pixelLevelsText.text())
        except Exception as error:
            self.statusText.setText(repr(error))
        self.event.set()

    def decompress(self,data,codec,compressed,uncompressed) :
        codecName = codec['name']
        if codecName!=self.codecName : 
            self.codecName = codecName
            self.codecNameText.setText(self.codecName)
        typevalue = codec['parameters']
        if typevalue== 1 : datatype = "int8"; elementsize =int(1)
        elif typevalue== 5 : datatype = "uint8"; elementsize =int(1)
        elif typevalue== 2 : datatype = "int16"; elementsize =int(2)
        elif typevalue== 6 : datatype = "uint16"; elementsize =int(2)
        elif typevalue== 3 : datatype = "int32"; elementsize =int(4)
        elif typevalue== 7 : datatype = "uint32"; elementsize =int(4)
        elif typevalue== 4 : datatype = "int64"; elementsize =int(8)
        elif typevalue== 8 : datatype = "uint64"; elementsize =int(8)
        elif typevalue== 9 : datatype = "float32"; elementsize =int(4)
        elif typevalue== 10 : datatype = "float64"; elementsize =int(8)
        else : raise Exception('decompress mapIntToType failed')
        if codecName=='blosc':
            lib = self.findLibrary.find(codecName)
        elif codecName=='jpeg' :
            lib = self.findLibrary.find('decompressJPEG')
        elif codecName=='lz4' or codecName=='bslz4' :
            lib = self.findLibrary.find('bitshuffle')
        else : lib = None
        if lib==None : raise Exception('shared library ' +codecName + ' not found')
        inarray = bytearray(data)
        in_char_array = ctypes.c_ubyte * compressed
        out_char_array = ctypes.c_ubyte * uncompressed
        outarray = bytearray(uncompressed)
        if codecName=='blosc' : 
            lib.blosc_decompress(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),uncompressed)
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=datatype)
        elif codecName=='lz4' :
            lib.LZ4_decompress_fast(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),uncompressed)
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=datatype)
        elif codecName=='bslz4' :
            lib.bshuf_decompress_lz4(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),int(uncompressed/elementsize),
                 elementsize,int(0))
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=datatype)
        elif codecName=='jpeg' :
            lib.decompressJPEG(
                 in_char_array.from_buffer(inarray),compressed,
                 out_char_array.from_buffer(outarray),uncompressed)
            data = np.array(outarray)
            data = data.flatten()
        else : raise Exception(codecName + " is unsupported codec")
        ratio = round(float(uncompressed/compressed))
        if ratio!=self.compressRatio :
            self.compressRatio = ratio
            self.compressRatioText.setText(str(self.compressRatio))
        return data

    def dataToImage(self,data,dimArray) :
        ny = 0
        nx = 0
        nz = 1
        datatype = str(data.dtype)
        ndim = len(dimArray)
        if ndim!=2 and ndim!=3 :
            raise Exception('ndim not 2 or 3')
            return
        if ndim ==2 :
            nx = dimArray[0]["size"]
            ny = dimArray[1]["size"]
            image = np.reshape(data,(ny,nx))
            image = np.transpose(image)
        elif ndim ==3 :
            if dimArray[0]["size"]==3 :
                nz = dimArray[0]["size"]
                nx = dimArray[1]["size"]
                ny = dimArray[2]["size"]
                image = np.reshape(data,(ny,nx,nz))
                image = np.transpose(image,(1,0,2))
            elif dimArray[1]["size"]==3 :
                nz = dimArray[1]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[2]["size"]
                image = np.reshape(data,(ny,nz,nx))
                image = np.swapaxes(image,2,1)
                image = np.transpose(image,(1,0,2))
            elif dimArray[2]["size"]==3 :
                nz = dimArray[2]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[1]["size"]
                image = np.reshape(data,(nz,ny,nx))
                image = np.swapaxes(image,0,2)
                image = np.swapaxes(image,0,1)
                image = np.transpose(image,(1,0,2))
            else  :  
                raise Exception('no axis has dim = 3')
                return
        else :
                raise Exception('ndim not 2 or 3')

        if datatype!=self.datatype :
            self.datatype = datatype
            self.dtypeText.setText(self.datatype)
            if datatype==str("int8") :
                pixelLevels = (int(-128),int(127))
            elif datatype==str("uint8") :
                pixelLevels = (int(0),int(255))
            elif datatype==str("int16") :
                pixelLevels = (int(-32768),int(32767))
            elif datatype==str("uint16") :
                pixelLevels = (int(0),int(65536))
            elif datatype==str("int32") :
                pixelLevels = (int(-2147483648),int(2147483647))
            elif datatype==str("uint32") :
                pixelLevels = (int(0),int(4294967296))
            elif datatype==str("int64") :
                pixelLevels = (int(-9223372036854775808),int(9223372036854775807))
            elif datatype==str("uint64") :
                pixelLevels = (int(0),int(18446744073709551615))
            elif datatype==str("float32") :
                pixelLevels = (float(0.0),float(1.0))
            elif datatype==str("float64") :
                pixelLevels = (float(0.0),float(1.0))
            else :
                raise Exception('unknown datatype' + datatype)
                return
            self.pixelLevelsText.setText(str(pixelLevels))
            self.imageDisplay.pixelLevels = pixelLevels
        if ny <self.minsize or nx<self.minsize :
            raise Exception('ny <',self.minsize,' or nx<',self.minsize)
        if nx!=self.nx :
            self.nx = nx
            self.nxText.setText(str(self.nx))
        if ny!=self.ny :
            self.ny = ny
            self.nyText.setText(str(self.ny))
        if nz!=self.nz :
            self.nz = nz
            self.nzText.setText(str(self.nz))
        width = nx
        height = ny
        if width==height :
            if width>self.maxsize : width = self.maxsize
            if height>self.maxsize : height = self.maxsize
        elif width<height :
            ratio = width/height
            if height>self.maxsize : height = self.maxsize
            width = height*ratio
        else :
            ratio = height/width
            if width>self.maxsize : width = self.maxsize
            height = width*ratio
        self.width = width
        self.height = height
        if self.imageDisplay.isHidden : 
            self.imageDisplay.width = width
            self.imageDisplay.height = height
        return image

    def p4pCallback(self,arg) :
        self.arg = arg;
        self.callbacksignal.emit()
        self.callbackDoneEvent.wait()
        self.callbackDoneEvent.clear()

    def mycallback(self):
        arg = self.arg
        argtype = str(type(arg))
        if argtype.find('Disconnected')>=0 :
            self.channelNameLabel.setStyleSheet("background-color:red")
            self.statusText.setText('disconnected')
            self.callbackDoneEvent.set()
            return
        else : self.channelNameLabel.setStyleSheet("background-color:green")
        value = None
        try:
            data = arg['value']
        except Exception as error:
            self.statusText.setText(repr(error))
            self.callbackDoneEvent.set()
            return
        dimArray = None
        try:
            dimArray = arg['dimension']
            compressed = arg['compressedSize']
            uncompressed = arg['uncompressedSize']
            codec = arg['codec']
            codecName = codec['name']
            codecNameLength = len(codecName)
        except Exception as error:
            self.statusText.setText(repr(error))
            self.callbackDoneEvent.set()
            return
        ndim = len(dimArray)
        if ndim!=2 and ndim!=3 :
            self.statusText.setText('ndim not 2 or 3')
            self.callbackDoneEvent.set()
            return
        if codecNameLength == 0 : 
            codecName = 'none'
            if codecName!=self.codecName : 
                self.codecName = codecName
                self.codecNameText.setText(self.codecName)
            ratio = round(1.0)
            if ratio!=self.compressRatio :
                self.compressRatio = ratio
                self.compressRatioText.setText(str(self.compressRatio))
            datatype = data.dtype
        self.event.wait()
        try:
            if codecNameLength != 0 : 
                data = self.decompress(data,codec,compressed,uncompressed)
            image = self.dataToImage(data,dimArray)
            args = (image,self.width,self.height)
            self.imageDisplay.newImage(args)
#            ret = self.metaObject.invokeMethod(self.imageDisplay, "newImage",
#                            Qt.BlockingQueuedConnection, Q_RETURN_ARG(int), Q_ARG(tuple,args))
        except Exception as error:
            self.statusText.setText(repr(error))
        self.nImages = self.nImages + 1
        self.timenow = time.time()
        timediff = self.timenow - self.lasttime
        if(timediff>1) :
            self.imageRateText.setText(str(round(self.nImages/timediff)))
            self.lasttime = self.timenow 
            self.nImages = 0
        self.event.set()
        self.callbackDoneEvent.set()

    def start(self) :
        self.channelNameText.setEnabled(False)
        self.subscription = self.ctxt.monitor(
              self.channelName,
              self.p4pCallback,
              request='field(value,codec,compressedSize,uncompressedSize,dimension)',
              notify_disconnect=True)
        self.isStarted = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.pixelLevelsText.setEnabled(True)
        self.channelNameText.setEnabled(False)

    def stop(self) :
        self.isStarted = False
        self.subscription.close()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.pixelLevelsText.setEnabled(False)
        self.channelNameLabel.setStyleSheet("background-color:gray")
        self.channelNameText.setEnabled(True)
        self.channel = None

    def createFirstRow(self) :
        box = QHBoxLayout()
        box.addWidget(self.startButton)
        box.addWidget(self.stopButton)
        
        box.addWidget(self.channelNameLabel)
        box.addWidget(self.channelNameText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.firstRow = wid

    def createSecondRow(self) :
        box = QHBoxLayout()
        nxLabel = QLabel("nx:")
        nxLabel.setFixedWidth(20)
        self.nxText.setText('0')
        box.addWidget(nxLabel)
        box.addWidget(self.nxText)
        nyLabel = QLabel("ny:")
        nyLabel.setFixedWidth(20)
        self.nyText.setText('0')
        box.addWidget(nyLabel)
        box.addWidget(self.nyText)
        nzLabel = QLabel("nz:")
        nzLabel.setFixedWidth(20)
        self.nzText.setText('0')
        box.addWidget(nzLabel)
        box.addWidget(self.nzText)
        dtypeLabel = QLabel("dtype:")
        box.addWidget(dtypeLabel)
        box.addWidget(self.dtypeText)

        codecNameLabel = QLabel("codec:")
        box.addWidget(codecNameLabel)
        box.addWidget(self.codecNameText)
        self.codecNameText.setText("none")

        compressRatioLabel = QLabel("compressRatio:")
        box.addWidget(compressRatioLabel)
        box.addWidget(self.compressRatioText)
        imageRateLabel = QLabel("imageRate:")
        box.addWidget(imageRateLabel)
        box.addWidget(self.imageRateText)
        pixelLevelsLabel = QLabel("pixel levels")
        box.addWidget(pixelLevelsLabel)
        box.addWidget(self.pixelLevelsText)

        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.secondRow = wid

    def createThirdRow(self) :
        box = QHBoxLayout()
        box.addWidget(self.clearButton)
        statusLabel = QLabel("  status:")
        statusLabel.setFixedWidth(50)
        box.addWidget(statusLabel)
        box.addWidget(self.statusText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.thirdRow = wid

    def initUI(self):
        self.setGeometry(1, 1, 1000, 40)
        self.createFirstRow()
        self.createSecondRow()
        self.createThirdRow()
        layout = QGridLayout()
        layout.addWidget(self.firstRow,0,0)
        layout.addWidget(self.secondRow,1,0)
        layout.addWidget(self.thirdRow,2,0)
        self.statusText.setText('nothing done so far')
        self.setLayout(layout)
        self.show()
        self.channelNameText.setText(self.channelName)
        self.startButton.clicked.connect(self.startEvent)
        self.stopButton.clicked.connect(self.stopEvent)
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        self.pixelLevelsText.editingFinished.connect(self.pixelLevelsEvent)
        self.clearButton.clicked.connect(self.clearEvent)
        self.imageDisplay = ImageDisplay()
#        self.metaObject = self.imageDisplay.metaObject()
        
        self.arg = None
        self.callbacksignal.connect(self.mycallback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    channelName = ''
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
    viewer = PY_NTNDA_Viewer(channelName)
    sys.exit(app.exec_())

