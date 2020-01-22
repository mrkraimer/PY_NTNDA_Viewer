#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *
import threading
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

import ctypes
import ctypes.util
import os

#from ast import literal_eval as make_tuple

class ImageDisplay(RawImageWidget):
    def __init__(self,viewer, parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent,scaled=True)
        self.viewer = viewer
        self.setWindowTitle('ImageDisplay')
        self.left = 1
        self.top = 300
        self.maxsize = 1080 - self.top
        self.viewer.maxsizeText.setText(str(self.maxsize))
        self.minsize = 16
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.width = self.maxsize
        self.height = self.maxsize
        self.datatype = 'none'
        self.pixelLevels = (0,0)
        self.lasttime = time.time() -2
        self.nImages = 0
        self.okToClose = False
        self.isHidden = True

    def closeEvent(self, event) :
        if not self.okToClose :
            event.ignore()
            self.isHidden = True
            self.hide()

    def setMaxsize(self,maxsize) :
        self.maxsize = maxsize

    def setPixelLevels(self,pixelLevels) :
        try :
           self.pixelLevels = make_tuple(pixelLevels)
        except Exception as error:
           self.viewer.statusText.setText("setPixelLevels error=" + repr(error))
        
    def newImage(self,image,dimArray):
        ny = 0
        nx = 0
        nz = 1
        datatype = str(image.dtype)
        ndim = len(dimArray)
        if ndim!=2 and ndim!=3 :
            raise Exception('ndim not 2 or 3')
            return
        if ndim ==2 :
            nx = dimArray[0]["size"]
            ny = dimArray[1]["size"]
            image = np.reshape(image,(ny,nx))
            image = np.transpose(image)
        elif ndim ==3 :
            if dimArray[0]["size"]==3 :
                nz = dimArray[0]["size"]
                nx = dimArray[1]["size"]
                ny = dimArray[2]["size"]
                image = np.reshape(image,(ny,nx,nz))
                image = np.transpose(image,(1,0,2))
            elif dimArray[1]["size"]==3 :
                nz = dimArray[1]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[2]["size"]
                image = np.reshape(image,(ny,nz,nx))
                image = np.swapaxes(image,2,1)
                image = np.transpose(image,(1,0,2))
            elif dimArray[2]["size"]==3 :
                nz = dimArray[2]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[1]["size"]
                image = np.reshape(image,(nz,ny,nx))
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
            self.viewer.dtypeText.setText(self.datatype)
            if datatype==str("int8") :
                self.pixelLevels = (int(-128),int(127))
            elif datatype==str("uint8") :
                self.pixelLevels = (int(0),int(255))
            elif datatype==str("int16") :
                self.pixelLevels = (int(-32768),int(32767))
            elif datatype==str("uint16") :
                self.pixelLevels = (int(0),int(65536))
            elif datatype==str("int32") :
                self.pixelLevels = (int(-2147483648),int(2147483647))
            elif datatype==str("uint32") :
                self.pixelLevels = (int(0),int(4294967296))
            elif datatype==str("int64") :
                self.pixelLevels = (int(-9223372036854775808),int(9223372036854775807))
            elif datatype==str("uint64") :
                self.pixelLevels = (int(0),int(18446744073709551615))
            elif datatype==str("float32") :
                self.pixelLevels = (float(0.0),float(1.0))
            elif datatype==str("float64") :
                self.pixelLevels = (float(0.0),float(1.0))
            else :
                raise Exception('unknown datatype' + datatype)
                return
            self.viewer.pixelLevelsText.setText(str(self.pixelLevels))
        if ny <self.minsize or nx<self.minsize :
            raise Exception('ny <',self.minsize,' or nx<',self.minsize)
        if nx!=self.nx :
            self.nx = nx
            self.viewer.nxText.setText(str(self.nx))
        if ny!=self.ny :
            self.ny = ny
            self.viewer.nyText.setText(str(self.ny))
        if nz!=self.nz :
            self.nz = nz
            self.viewer.nzText.setText(str(self.nz))
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
        if self.isHidden or (height!=self.height) or (width!=self.width) :
            self.width = width
            self.height = height
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.viewer.widthText.setText(str(self.width))
            self.viewer.heightText.setText(str(self.height))
        if self.isHidden : 
            self.isHidden = False
            self.show()
        self.setImage(image,levels=self.pixelLevels)
        self.nImages = self.nImages + 1
        self.timenow = time.time()
        timediff = self.timenow - self.lasttime
        if(timediff<1) : return        
        images = self.nImages/timediff
        imgfmt = '{0:.2f}'.format(images)
        text =  imgfmt + "/sec"
        self.viewer.imageRateText.setText(text)
        self.lasttime = self.timenow 
        self.nImages = 0

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
    def __init__(self,channelName, parent=None):
        super(QWidget, self).__init__(parent)
        self.channelName = channelName
        self.event = threading.Event()
        self.event.set()
        self.setWindowTitle("PY_NTNDA_Viewer")
        self.getChannel = GetChannel()
        self.findLibrary = FindLibrary()
# first row
        self.startButton = QPushButton('start')
        self.startButton.setEnabled(True)
        self.stopButton = QPushButton('stop')
        self.stopButton.setEnabled(False)
        self.channelNameText = QLineEdit()
        self.channelNameText.setEnabled(True)
        
        self.channel = None
        self.isStarted = False
# second row
        self.maxsizeText = QLineEdit()
        self.maxsizeText.setFixedWidth(50)
        self.nxText = QLabel()
        self.nxText.setFixedWidth(50)
        self.nyText = QLabel()
        self.nyText.setFixedWidth(50)
        self.nzText = QLabel()
        self.nzText.setFixedWidth(50)
        self.widthText = QLabel()
        self.widthText.setFixedWidth(50)
        self.heightText = QLabel()
        self.heightText.setFixedWidth(50)
        self.imageRateText = QLabel()
# third row
        self.dtypeText = QLabel()
        self.codecNameText = QLabel()
        self.compressedSizeText = QLabel()
        self.uncompressedSizeText = QLabel()
        self.pixelLevelsText = QLineEdit()
        self.pixelLevelsText.setEnabled(False)
# fourth row
        self.clearButton = QPushButton('clear')
        self.clearButton.setEnabled(True)
        self.statusText = QLineEdit()
# initialize
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

    def maxsizeEvent(self) :
        self.event.wait()
        try:
            maxsize = int(self.maxsizeText.text())
            self.imageDisplay.setMaxsize(maxsize)
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

    def mycallback(self,arg):
        value = None
        try:
            value = arg['value'][0]
        except Exception as error:
            self.statusText.setText(repr(error))
            return
        try :
            if len(value) != 1 :
                self.statusText.setText('value length not 1')
                return
            element = None
            for x in value :
                element = x
            if element == None : 
                self.statusText.setText('value is not numpyarray')
            else :
                data = value[element]
        except Exception as error:
            self.statusText.setText(repr(error))
            return
        dimArray = None
        try:
            dimArray = arg['dimension']
        except Exception as error:
            self.statusText.setText(repr(error))
            return
        compressed = arg['compressedSize']
        uncompressed = arg['uncompressedSize']
        codec = arg['codec']
        codecName = codec['name']
        parameters = codec['parameters']
        typevalue = parameters[0]['value']
        if typevalue== 1 : datatype = "int8"; elementsize =1
        elif typevalue== 2 : datatype = "int16"; elementsize =2
        elif typevalue== 3 : datatype = "int32"; elementsize =4
        elif typevalue== 4 : datatype = "int64"; elementsize =8
        elif typevalue== 5 : datatype = "uint8"; elementsize =1
        elif typevalue== 6 : datatype = "uint16"; elementsize =2
        elif typevalue== 7 : datatype = "uint32"; elementsize =4
        elif typevalue== 8 : datatype = "uint64"; elementsize =8
        elif typevalue== 9 : datatype = "float32"; elementsize =4
        elif typevalue== 10 : datatype = "float64"; elementsize =8
        else : raise Exception('mapIntToType')
        if len(codecName) == 0 : 
            codecName = 'none'
            compressed = uncompressed
        else :
            if codecName=='blosc':
                lib = self.findLibrary.find(codecName)
            elif codecName=='jpeg' :
                lib = self.findLibrary.find('decompressJPEG')
            elif codecName=='lz4' or codecName=='bslz4' :
                lib = self.findLibrary.find('bitshuffle')
            else : lib = None
            if lib==None :
                self.statusText.setText('shared library ' +codecName + ' not found')
                return
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
                     elementsize,0)
                data = np.array(outarray)
                data = np.frombuffer(data,dtype=datatype)
            elif codecName=='jpeg' :
                lib.decompressJPEG(
                     in_char_array.from_buffer(inarray),compressed,
                     out_char_array.from_buffer(outarray),uncompressed)
                data = np.array(outarray)
                data = data.flatten()
            else :
                self.statusText.setText(codecName + " is unsupported codec")
                return
        self.codecNameText.setText(codecName)
        self.compressedSizeText.setText(str(compressed))
        self.uncompressedSizeText.setText(str(uncompressed))
        self.event.wait()
        try:
            self.imageDisplay.newImage(data,dimArray)
        except Exception as error:
            self.statusText.setText(repr(error))
        self.event.set()

    def start(self) :
        self.channelNameText.setEnabled(False)
        self.channel = self.getChannel.get(self.channelName)
        self.channel.monitor(self.mycallback,'field()')
        self.isStarted = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.pixelLevelsText.setEnabled(True)
        self.channelNameText.setEnabled(False)

    def stop(self) :
        self.isStarted = False
        self.channel.stopMonitor()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.pixelLevelsText.setEnabled(False)
        self.channelNameText.setEnabled(True)
        self.channel = None

    def createFirstRow(self) :
        box = QHBoxLayout()
        box.addWidget(self.startButton)
        box.addWidget(self.stopButton)
        channelNameLabel = QLabel("channelName:")
        box.addWidget(channelNameLabel)
        box.addWidget(self.channelNameText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.firstRow = wid

    def createSecondRow(self) :
        box = QHBoxLayout()
        maxsizeLabel = QLabel("maxsize:")
        maxsizeLabel.setFixedWidth(60)
        box.addWidget(maxsizeLabel)
        box.addWidget(self.maxsizeText)
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
        widthLabel = QLabel("width:")
        widthLabel.setFixedWidth(40)
        box.addWidget(widthLabel)
        box.addWidget(self.widthText)
        heightLabel = QLabel("height:")
        heightLabel.setFixedWidth(60)
        box.addWidget(heightLabel)
        box.addWidget(self.heightText)
        imageRateLabel = QLabel("imageRate:")
        imageRateLabel.setFixedWidth(90)
        box.addWidget(imageRateLabel)
        box.addWidget(self.imageRateText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.secondRow = wid

    def createThirdRow(self) :
        box = QHBoxLayout()
        dtypeLabel = QLabel("dtype:")
        box.addWidget(dtypeLabel)
        box.addWidget(self.dtypeText)
        self.dtypeText.setFixedWidth(60)

        codecNameLabel = QLabel("codec:")
        box.addWidget(codecNameLabel)
        box.addWidget(self.codecNameText)
        self.codecNameText.setFixedWidth(60)
        self.codecNameText.setText("none")

        compressedSizeLabel = QLabel("compressed:")
        box.addWidget(compressedSizeLabel)
        box.addWidget(self.compressedSizeText)
        self.compressedSizeText.setFixedWidth(100)

        uncompressedSizeLabel = QLabel("uncompressed:")
        box.addWidget(uncompressedSizeLabel)
        box.addWidget(self.uncompressedSizeText)
        self.uncompressedSizeText.setFixedWidth(100)

        pixelLevelsLabel = QLabel("pixel levels")
        pixelLevelsLabel.setFixedWidth(80)
        box.addWidget(pixelLevelsLabel)
        box.addWidget(self.pixelLevelsText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.thirdRow = wid

    def createFourthRow(self) :
        box = QHBoxLayout()
        box.addWidget(self.clearButton)
        statusLabel = QLabel("  status:")
        statusLabel.setFixedWidth(50)
        box.addWidget(statusLabel)
        box.addWidget(self.statusText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.fourthRow = wid

    def initUI(self):
        self.setGeometry(1, 1, 900, 40)
        self.createFirstRow()
        self.createSecondRow()
        self.createThirdRow()
        self.createFourthRow()
        layout = QGridLayout()
        layout.addWidget(self.firstRow,0,0)
        layout.addWidget(self.secondRow,1,0)
        layout.addWidget(self.thirdRow,2,0)
        layout.addWidget(self.fourthRow,3,0)
        self.statusText.setText('nothing done so far')
        self.setLayout(layout)
        self.show()
        self.channelNameText.setText(self.channelName)
        self.startButton.clicked.connect(self.startEvent)
        self.stopButton.clicked.connect(self.stopEvent)
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        self.maxsizeText.editingFinished.connect(self.maxsizeEvent)
        self.pixelLevelsText.editingFinished.connect(self.pixelLevelsEvent)
        self.clearButton.clicked.connect(self.clearEvent)
        self.imageDisplay = ImageDisplay(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    channelName = ''
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
    viewer = PY_NTNDA_Viewer(channelName)
    sys.exit(app.exec_())

