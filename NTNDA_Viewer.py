# NTNDA_Viewer.py

import sys,time,signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import numpy as np
from p4p.client.thread import Context
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit,QSlider
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from PyQt5.QtCore import *

import ctypes
import ctypes.util
import os

from NTNDA_Channel_Provider import NTNDA_Channel_Provider

from NTNDA_RawImage_Display import NTNDA_RawImage_Display
from NTNDA_ZoomImage_Display import NTNDA_ZoomImage_Display


class ImageControl(QWidget) :
    def __init__(self,  name,left,top,parent=None, **kargs):
        super(QWidget, self).__init__(parent)
        self.setObjectName(name)
        self.name = name
        self.left = left
        self.top = top
        self.ignoreClose = True
        self.okToClose = False
        self.isHidden = True
        self.rawImageDisplay = NTNDA_RawImage_Display(name + ' raw image',self.left,self.top)
        self.zoomImageDisplay = NTNDA_ZoomImage_Display(name + ' zoom image',self.left,self.top)
        self.arg = None      
        self.npixelLevels = 255
        self.windowTitle = name + ' Control'
        self.dtype = ""
        self.minimum = 0;
        self.low = 0
        self.high = self.npixelLevels
        self.maximum = self.npixelLevels
        self.okToClose = False
        self.isHidden = False
        self.arg = None
        self.pixelLevels = (int(0),int(255))
# title row
        value = '{:>85}'.format(name) + ' control       '
        titleLabel = QLabel(value)
        self.zoomImageButton = QPushButton('zoomImage')
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(titleLabel)
        box.addWidget(self.zoomImageButton)
        wid =  QWidget()
        wid.setLayout(box)
        self.titleRow = wid
# first row
        minimumLabel = QLabel("minimum")
        minimumLabel.setFixedWidth(150)
        lowLabel = QLabel("low")
        lowLabel.setFixedWidth(150)
        highLabel = QLabel("high")
        highLabel.setFixedWidth(150)
        maximumLabel = QLabel("maximum")
        maximumLabel.setFixedWidth(150)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(minimumLabel)
        box.addWidget(lowLabel);
        box.addWidget(highLabel);
        box.addWidget(maximumLabel)
        wid =  QWidget()
        wid.setLayout(box)
        self.firstRow = wid
#second row
        self.minimumText = QLineEdit()
        self.minimumText.setText('')
        self.minimumText.setEnabled(True)
        self.minimumText.setFixedWidth(150)
        self.minimumText.editingFinished.connect(self.minimumEvent)
        self.lowText = QLabel('')
        self.lowText.setFixedWidth(150)
        self.highText = QLabel('')
        self.highText.setFixedWidth(150)
        self.maximumText = QLineEdit()
        self.maximumText.setFixedWidth(150)
        self.maximumText.editingFinished.connect(self.maximumEvent)
        self.maximumText.setEnabled(True)
        self.maximumText.setText('')
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.minimumText)
        box.addWidget(self.lowText)
        box.addWidget(self.highText)
        box.addWidget(self.maximumText)
        wid =  QWidget()
        wid.setLayout(box)
        self.secondRow = wid
#third row
        self.lowSlider = QSlider(Qt.Horizontal)
        self.lowSlider.setMinimum(0)
        self.lowSlider.setMaximum(self.npixelLevels)
        self.lowSlider.setValue(0)
        self.lowSlider.setTickPosition(QSlider.TicksBelow)
        self.lowSlider.setTickInterval(10)
        self.lowSlider.setFixedWidth(300)
        self.highSlider = QSlider(Qt.Horizontal)
        self.highSlider.setMinimum(0)
        self.highSlider.setMaximum(self.npixelLevels)
        self.highSlider.setValue(self.npixelLevels)
        self.highSlider.setTickPosition(QSlider.TicksBelow)
        self.highSlider.setTickInterval(10)
        self.highSlider.setFixedWidth(300)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.lowSlider)
        box.addWidget(self.highSlider)
        wid =  QWidget()
        wid.setLayout(box)
        self.thirdRow = wid
#create window
        layout = QGridLayout()
        layout.setSpacing(0);
        layout.addWidget(self.titleRow,0,0)
        layout.addWidget(self.firstRow,1,0)
        layout.addWidget(self.secondRow,2,0)
        layout.addWidget(self.thirdRow,3,0)
        self.setLayout(layout)
        self.setWindowTitle(self.windowTitle)
        self.lowSlider.valueChanged.connect(self.lowSliderValueChange)
        self.highSlider.valueChanged.connect(self.highSliderValueChange)

    def minimumEvent(self) :
        try:
            minimum = float(self.minimumText.text())
            if minimum>self.maximum :
                minimum = self.maximum
                self.minimumText.setText(str(minimum))
            if minimum>self.low :
                self.low = minimum
                self.lowText.setText(str(self.low))
        except Exception as error:
            self.minimumText.setText(repr(error))

    def maximumEvent(self) :
        try:
            maximum = float(self.maximumText.text())
            if maximum<self.minimum :
                maximum = self.minimum
                self.maximumText.setText(str(maximum))
            if maximum<self.high :
                self.high = maximum
                self.highText.setText(str(self.high))
        except Exception as error:
            self.maximumText.setText(repr(error))

    def getPixelLevels(self) :
        return (self.low,self.high)

    def setDtype(self,datatype) :
        if datatype==self.dtype : return
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
        self.rawImageDisplay.setPixelLevels(self.pixelLevels);
        self.minimum = self.pixelLevels[0]
        self.minimumText.setText(str(self.minimum))
        self.low = self.minimum
        self.lowText.setText(str(self.low))
        self.maximum  = self.pixelLevels[1]
        self.maximumText.setText(str(self.maximum))
        self.high = self.maximum
        self.highText.setText(str(self.high))
        self.lowSlider.setValue(0)
        self.highSlider.setValue(self.npixelLevels)

    def closeEvent(self, event) :
        if not self.okToClose : 
            event.ignore()
            self.hide()
        self.rawImageDisplay.okToClose = True
        self.rawImageDisplay.hide()
        self.zoomImageDisplay.okToClose = True
        self.zoomImageDisplay.hide()

    def lowSliderValueChange(self) :
        pixelRatio = float(self.lowSlider.value())/float(self.npixelLevels)
        valueRange = float(self.maximum) - float(self.minimum)
        value = pixelRatio*valueRange + self.minimum
        if value>self.maximum : value = self.maximum
        if value>self.high :
            self.high = value
            self.highText.setText(str(self.high))
        self.low= value
        self.lowText.setText(str(self.low))
        self.setPixelLevels((self.low,self.high))
        self.rawImageDisplay.display()
        
    def highSliderValueChange(self) :
        pixelRatio = float(self.highSlider.value())/float(self.npixelLevels)
        valueRange = float(self.maximum) - float(self.minimum)
        value = pixelRatio*valueRange + self.minimum
        if value<self.minimum : value = self.minimum
        if value<self.low :
            self.low = value
            self.lowText.setText(str(self.low))
        self.high = value
        self.highText.setText(str(self.high))
        self.setPixelLevels((self.low,self.high))
        self.rawImageDisplay.display()
        
    def setPixelLevels(self,pixelLevels) :
        self.pixelLevels = pixelLevels
        self.rawImageDisplay.setPixelLevels(self.pixelLevels)

    def newImage(self,arg):
        self.arg = arg
        self.rawImageDisplay.newImage(arg)

    def display(self) :
        self.rawImageDisplay.display()

    def zoomImage(self) :
        if self.arg==None : return
        self.zoomImageDisplay.setPixelLevels(self.pixelLevels);
        self.zoomImageDisplay.newImage(self.arg)
        self.zoomImageDisplay.display()

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

class NTNDA_Viewer(QWidget) :
    def __init__(self,provider,providerName, parent=None):
        super(QWidget, self).__init__(parent)
        self.provider = provider
        self.provider.NTNDA_Viewer = self
        self.windowTitle = providerName + "_NTNDA_Viewer"
        self.image = ()
# first row
        self.startButton = QPushButton('start')
        self.startButton.setEnabled(True)
        self.startButton.clicked.connect(self.startEvent)
        self.isStarted = False
        self.stopButton = QPushButton('stop')
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stopEvent)
        self.snapButton = QPushButton('snap')
        self.snapButton.setEnabled(True)
        self.snapButton.clicked.connect(self.snapEvent)
        if len(self.provider.getChannelName())<1 :
            name = os.getenv('EPICS_NTNDA_VIEWER_CHANNELNAME')
            if name!= None : self.provider.setChannelName(name)
        self.channelNameLabel = QLabel("channelName:")
        self.channelNameText = QLineEdit()
        self.channelNameText.setEnabled(True)
        self.channelNameText.setText(self.provider.getChannelName())
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.startButton)
        box.addWidget(self.stopButton)
        box.addWidget(self.snapButton)
        box.addWidget(self.channelNameLabel)
        box.addWidget(self.channelNameText)
        wid =  QWidget()
        wid.setLayout(box)
        self.firstRow = wid
# second row
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.nxText = QLabel()
        self.nxText.setFixedWidth(50)
        self.nyText = QLabel()
        self.nyText.setFixedWidth(50)
        self.nzText = QLabel()
        self.nzText.setFixedWidth(20)
        self.datatype = None
        self.dtypeText = QLabel()
        self.dtypeText.setFixedWidth(50)
        self.codecName = ''
        self.codecNameText = QLabel()
        self.codecNameText.setFixedWidth(40)
        self.compressRatioText = QLabel()
        self.compressRatioText.setFixedWidth(40)
        self.nImages = 0
        self.imageRateText = QLabel()
        self.imageRateText.setFixedWidth(40)
        self.compressRatio = round(1.0)
        self.compressRatioText.setText(str(self.compressRatio))
        self.clearButton = QPushButton('clear')
        self.clearButton.setEnabled(True)
        self.clearButton.clicked.connect(self.clearEvent)    
        self.statusText = QLineEdit()
        self.statusText.setText('nothing done so far')
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
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
        box.addWidget(self.clearButton)
        statusLabel = QLabel("  status:")
        statusLabel.setFixedWidth(50)
        box.addWidget(statusLabel)
        box.addWidget(self.statusText)
        wid =  QWidget()
        wid.setLayout(box)
        self.secondRow = wid
# third row
        self.dynamicDisplay = ImageControl('dynamic',10,300)
        self.dynamicDisplay.zoomImageButton.clicked.connect(self.changeDynamicImageEvent)
        self.snapDisplay = ImageControl('snap',600,300)
        self.snapDisplay.zoomImageButton.clicked.connect(self.changeSnapImageEvent)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.dynamicDisplay)
        box.addWidget(self.snapDisplay)
        wid =  QWidget()
        wid.setLayout(box)
        self.thirdRow = wid
# initialize
        layout = QGridLayout()
        layout.setVerticalSpacing(0);
        layout.addWidget(self.firstRow,0,0)
        layout.addWidget(self.secondRow,1,0)
        layout.addWidget(self.thirdRow,2,0)
        self.setLayout(layout)
        self.setWindowTitle(self.windowTitle)
        self.findLibrary = FindLibrary()
        self.subscription = None
        self.lasttime = time.time() -2
        self.maxsize = 800
        self.minsize = 16
        self.width = self.maxsize
        self.height = self.maxsize
        self.arg = None
        self.setGeometry(10, 40, 1000, 100)
        self.show()
        self.dynamicDisplay.show()
        self.snapDisplay.show()

    def closeEvent(self, event) :
        if self.isStarted : self.stop()
        self.dynamicDisplay.ignoreClose = False
        self.dynamicDisplay.close()
        self.snapDisplay.ignoreClose = False
        self.snapDisplay.close()
        self.provider.done()
        
    def startEvent(self) :
        self.start()

    def stopEvent(self) :
        self.stop()

    def clearEvent(self) :
        self.statusText.setText('')
    
    def channelNameEvent(self) :
        try:
            self.provider.setChannelName(self.channelNameText.text())
        except Exception as error:
            self.statusText.setText(repr(error))

    def snapEvent(self) :
        if len(self.image)<=0 : 
            self.statusText.setText("no image is available")
            return
        self.snapDisplay.setDtype(self.datatype)
        args = (self.image,self.width,self.height,self.nx,self.ny,self.nz)
        self.snapDisplay.newImage(args)
        self.snapDisplay.display()

    def changeDynamicImageEvent(self) :
        self.dynamicDisplay.zoomImage()

    def changeSnapImageEvent(self) :
        self.snapDisplay.zoomImage()

    def start(self) :
        self.provider.start()
        self.channelNameText.setEnabled(False)
        self.isStarted = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.channelNameText.setEnabled(False)

    def stop(self) :
        self.provider.stop()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.channelNameLabel.setStyleSheet("background-color:gray")
        self.channelNameText.setEnabled(True)
        self.channel = None
        self.isStarted = False

    def callback(self,arg):
        if len(arg)==1 :
            value = arg.get("exception")
            if value!=None :
                self.statusText.setText(repr(error))
                return
            value = arg.get("status")
            if value!=None :
                if value=="disconnected" :
                    self.channelNameLabel.setStyleSheet("background-color:red")
                    self.statusText.setText('disconnected')
                    return
                elif value=="connected" :
                    self.channelNameLabel.setStyleSheet("background-color:green")
                    self.statusText.setText('connected')
                    return
                else :
                    self.statusText.setText("unknown callback error")
                    return
        try:
            data = arg['value']
            dimArray = arg['dimension']
            compressed = arg['compressedSize']
            uncompressed = arg['uncompressedSize']
            codec = arg['codec']
            codecName = codec['name']
            codecNameLength = len(codecName)
        except Exception as error:
            self.statusText.setText(repr(error))
            return
        ndim = len(dimArray)
        if ndim!=2 and ndim!=3 :
            self.statusText.setText('ndim not 2 or 3')
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
        try:
            if codecNameLength != 0 : 
                data = self.decompress(data,codec,compressed,uncompressed)
            self.image = self.dataToImage(data,dimArray)
            args = (self.image,self.width,self.height,self.nx,self.ny,self.nz)
            self.dynamicDisplay.newImage(args)
            self.dynamicDisplay.display()
        except Exception as error:
            self.statusText.setText(repr(error))
        self.nImages = self.nImages + 1
        self.timenow = time.time()
        timediff = self.timenow - self.lasttime
        if(timediff>1) :
            self.imageRateText.setText(str(round(self.nImages/timediff)))
            self.lasttime = self.timenow 
            self.nImages = 0

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
            self.dynamicDisplay.setDtype(datatype)
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
        return image

