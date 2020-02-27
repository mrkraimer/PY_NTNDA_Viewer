# NTNDA_Viewer.py

import sys,time,signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
import numpy as np
from pyqtgraph.widgets.RawImageWidget import RawImageWidget
from PyQt5.QtWidgets import QWidget,QLabel,QLineEdit,QSlider
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout
from PyQt5.QtWidgets import QRubberBand
from PyQt5.QtCore import *

import ctypes
import ctypes.util
import os

class NTNDA_Channel_Provider(object) :
    '''
    Base class for monitoring an NTNDArray channel from an areaDetector IOC.
    The methods are called by NTNDA_Viewer.
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


def imageDictCreate() :
    return {"image" : None , "dtype" : "" , "nx" : 0 , "ny" : 0 ,  "nz" : 0 }

class Image_Display(RawImageWidget) :
    def __init__(self,parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent,scaled=True)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle,self)
        self.mousePressPosition = QPoint(0,0)
        self.mouseReleasePosition = QPoint(0,0)
        self.clientCallback = None
        self.mousePressed = False

    def display(self,image,pixelLevels) :
        self.setImage(image,levels=pixelLevels)
        self.show()

    def mousePressEvent(self,event) :
        self.mousePressPosition = QPoint(event.pos())
        self.rubberBand.setGeometry(QRect(self.mousePressPosition,QSize()))
        self.rubberBand.show()
        self.mousePressed = True

    def mouseMoveEvent(self,event) :
        if not self.mousePressed : return
        self.rubberBand.setGeometry(QRect(self.mousePressPosition,event.pos()).normalized())

    def mouseReleaseEvent(self,event) :
        if not self.mousePressed : return
        self.mouseReleasePosition = QPoint(event.pos())
        if not self.clientCallback==None : 
            self.clientCallback(self.mousePressPosition,self.mouseReleasePosition)
        self.rubberBand.hide()
        self.mousePressed = False

    def clientReleaseEvent(self,clientCallback) :
        self.clientCallback = clientCallback



class ImageControl(QWidget) :

    def __init__(self,  name,parent=None, **kargs):
        super(QWidget, self).__init__(parent)
        self.imageDisplay = Image_Display()
        self.imageDisplay.clientReleaseEvent(self.clientReleaseEvent)
        self.imageDict = imageDictCreate()
        self.name = name
        self.pixelLevels = (int(0),int(255))
        self.npixelLevels = 255
        self.minimum = 0;
        self.low = 0
        self.high = self.npixelLevels
        self.maximum = self.npixelLevels
        # following are for zoom image
        self.isZoomImage = False
        self.xlow = 0
        self.ylow = 0
        self.numx = 0
        self.numy = 0
# title row
        titleLabel = QLabel('{:>85}'.format(name) + ' image')
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(titleLabel)
        wid =  QWidget()
        wid.setLayout(box)
        self.titleRow = wid
# first row
        minimumLabel = QLabel("minimum")
        minimumLabel.setFixedWidth(100)
        lowLabel = QLabel("low")
        lowLabel.setFixedWidth(100)
        highLabel = QLabel("high")
        highLabel.setFixedWidth(100)
        maximumLabel = QLabel("maximum")
        maximumLabel.setFixedWidth(100)
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
        self.minimumText.setFixedWidth(100)
        self.minimumText.editingFinished.connect(self.minimumEvent)
        self.lowText = QLabel('')
        self.lowText.setFixedWidth(100)
        self.highText = QLabel('')
        self.highText.setFixedWidth(100)
        self.maximumText = QLineEdit()
        self.maximumText.setFixedWidth(100)
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
# zoom row
        titleLabel = QLabel(name+' zoom ')
        zoomLabel = QLabel('(xlow,ylow,numx.numy)')
        self.zoomText = QLineEdit()
        self.zoomText.setEnabled(True)
        self.zoomText.setFixedWidth(140)
        self.zoomText.editingFinished.connect(self.zoomTextEvent)
        self.resetButton = QPushButton('reset')
        self.resetButton.setEnabled(True)
        self.resetButton.clicked.connect(self.resetEvent)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(titleLabel)
        box.addWidget(zoomLabel)
        box.addWidget(self.zoomText)
        box.addWidget(self.resetButton)
        wid =  QWidget()
        wid.setLayout(box)
        self.zoomRow = wid
# image row
        self.size = 600
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.imageDisplay)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(self.size)
        wid.setFixedWidth(self.size)
        self.imageRow = wid
#create window
        layout = QGridLayout()
        layout.setSpacing(0);
        layout.addWidget(self.titleRow,0,0)
        layout.addWidget(self.firstRow,1,0)
        layout.addWidget(self.secondRow,2,0)
        layout.addWidget(self.thirdRow,3,0)
        layout.addWidget(self.zoomRow,4,0)
        layout.addWidget(self.imageRow,5,0)
        self.setLayout(layout)
        self.lowSlider.valueChanged.connect(self.lowSliderValueChange)
        self.highSlider.valueChanged.connect(self.highSliderValueChange)
        self.show()

    def resetEvent(self) :
        self.xlow = 0
        self.ylow = 0
        self.numx = self.imageDict["nx"]
        self.numy = self.imageDict["ny"]
        zoom = '(0,0,' + str(self.numx) + ',' + str(self.numy) + ')'
        self.zoomText.setText(zoom)
        self.isZoomImage = False
        self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)

    def clientReleaseEvent(self,pressPosition,releasePosition) :
        qrect = self.imageDisplay.geometry()
        height = qrect.height()
        width = qrect.width()
        xmin = pressPosition.x()
        ymin = pressPosition.y()
        xmax = releasePosition.x()
        ymax = releasePosition.y()
        if self.isZoomImage : 
            xstart = self.xlow
            ystart = self.ylow
            sizex = self.numx
            sizey = self.numy
        else :
            xstart = 0
            ystart = 0
            sizex = self.imageDict["nx"]
            sizey = self.imageDict["ny"]
        if (sizex/sizey)>1.0 :
            yfact = sizex/sizey
            xfact = 1.0
        elif (sizey/sizex)>1.0 :
            yfact = 1.0
            xfact = sizey/sizex
        else :
            yfact = 1.0
            xfact = 1.0
        ratiox = (sizex/width)*xfact
        ratioy = (sizey/height)*yfact
        xlow = int(xmin*ratiox) + self.xlow
        ylow = int(ymin*ratioy) + self.ylow
        numx = int((xmax-xmin)*ratiox)
        numy = int((ymax-ymin)*ratioy)       
        zoom = '(' + str(xlow) + ',' + str(ylow) + ',' + str(numx) + ',' + str(numy) + ')'
        self.zoomText.setText(zoom)
        self.zoomTextEvent()

    def zoomTextEvent(self) :
        try :
            text = self.zoomText.text()
            ind = text.find('(')
            if ind<0 : raise Exception('does not start with (')
            text = text[(ind+1):]
            ind = text.find(')')
            if ind<0 : raise Exception('does not end with )')
            text = text[:-1]
            split = text.split(',')
            if len(split)!=4 : raise Exception('not four values')
            xlow = int(split[0])
            ylow = int(split[1])
            numx = int(split[2])
            numy = int(split[3])
            if xlow<self.pixelLevels[0] : raise Exception('xlow bad')
            if ylow<self.pixelLevels[0] : raise Exception('ylow bad')
            if xlow>(self.imageDict["nx"]-16) : raise Exception('xlow bad')
            if ylow>(self.imageDict["ny"]-16) : raise Exception('ylow bad')
            if numx>(self.imageDict["nx"]-xlow) : raise Exception('numx bad')
            if numy>(self.imageDict["ny"]-ylow) : raise Exception('numy bad')
        except Exception as error:
            self.zoomText.setText(str(error))
            return
        self.xlow = xlow
        self.ylow = ylow
        self.numx = numx
        self.numy = numy
        self.isZoomImage = True
        self.displayZoom()

    def displayZoom(self) :
        fromimage = self.imageDict["image"]
        if self.imageDict["nz"]==1 :
            image = np.empty((self.numx,self.numy),dtype=self.imageDict["dtype"])
            for indx in range(0,self.numx) :
                for indy in range(0,self.numy) :
                    image[indx][indy] = fromimage[indx+self.xlow][indy+self.ylow]
        elif self.imageDict["nz"]==3 :
            image = np.empty((self.numx,self.numy,3),dtype=self.imageDict["dtype"])
            for indx in range(0,self.numx) :
                for indy in range(0,self.numy) :
                    for indz in range(0,3) :
                        image[indx][indy][indz] = fromimage[indx+self.xlow][indy+self.ylow][indz]
        else : raise Exception('ndim not 2 or 3')
        self.imageDisplay.display(image,self.pixelLevels)

    def minimumEvent(self) :
        try:
            minimum = float(self.minimumText.text())
            if minimum>self.maximum :
                minimum = self.maximum
                self.minimumText.setText(str(minimum))
            self.minimum = minimum
            self.low = minimum
            self.lowText.setText(str(self.low))
            self.pixelLevels = (self.low,self.high)
            self.lowSlider.setValue(0)
            if self.isZoomImage : self.displayZoom()
            else :self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)
        except Exception as error:
            self.minimumText.setText(str(error))

    def maximumEvent(self) :
        try:
            maximum = float(self.maximumText.text())
            if maximum<self.minimum :
                maximum = self.minimum
                self.maximumText.setText(str(maximum))
            self.maximum = maximum
            self.high = maximum
            self.highText.setText(str(self.high))
            self.pixelLevels = (self.low,self.high)
            self.highSlider.setValue(self.npixelLevels)
            if self.isZoomImage : self.displayZoom()
            else :self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)
        except Exception as error:
            self.maximumText.setText(str(error))

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
        self.pixelLevels = (self.low,self.high)
        if self.isZoomImage : self.displayZoom()
        else :self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)
        
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
        self.pixelLevels = (self.low,self.high)
        if self.isZoomImage : self.displayZoom()
        else :self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)

    def newImage(self,imageDict):
        self.imageDict["image"] = imageDict["image"]
        self.imageDict["nx"] = imageDict["nx"]
        self.imageDict["ny"] = imageDict["ny"]
        self.imageDict["nz"] = imageDict["nz"]
        if not str(imageDict["dtype"])==str(self.imageDict["dtype"]) :
            self.imageDict["dtype"] = imageDict["dtype"]
            dtype = self.imageDict["dtype"]
            if dtype==str("int8") :
                self.pixelLevels = (int(-128),int(127))
            elif dtype==str("uint8") :
                self.pixelLevels = (int(0),int(255))
            elif dtype==str("int16") :
                self.pixelLevels = (int(-32768),int(32767))
            elif dtype==str("uint16") :
                self.pixelLevels = (int(0),int(65536))
            elif dtype==str("int32") :
                self.pixelLevels = (int(-2147483648),int(2147483647))
            elif dtype==str("uint32") :
                self.pixelLevels = (int(0),int(4294967296))
            elif dtype==str("int64") :
                self.pixelLevels = (int(-9223372036854775808),int(9223372036854775807))
            elif dtype==str("uint64") :
                self.pixelLevels = (int(0),int(18446744073709551615))
            elif dtype==str("float32") :
                self.pixelLevels = (float(0.0),float(1.0))
            elif dtype==str("float64") :
                self.pixelLevels = (float(0.0),float(1.0))
            else :
                raise Exception('unknown dtype' + dtype)
                return
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
            zoom = '(0,0,' + str(self.imageDict["nx"]) + ',' + str(self.imageDict["ny"]) + ')'
            self.zoomText.setText(zoom)
            self.isZoomImage = False

    def display(self) :
        if self.isZoomImage :
            self.displayZoom()
            return
        self.imageDisplay.display(self.imageDict["image"],self.pixelLevels)
          
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
    def __init__(self,ntnda_Channel_Provider,providerName, parent=None):
        super(QWidget, self).__init__(parent)
        self.provider = ntnda_Channel_Provider
        self.provider.NTNDA_Viewer = self
        self.windowTitle = providerName + "_NTNDA_Viewer"
        self.imageDict = imageDictCreate()
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
        self.nxText = QLabel()
        self.nxText.setFixedWidth(50)
        self.nyText = QLabel()
        self.nyText.setFixedWidth(50)
        self.nzText = QLabel()
        self.nzText.setFixedWidth(20)
        self.dtype = None
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
        self.dynamicDisplay = ImageControl('dynamic')
        self.snapDisplay = ImageControl('snap')
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
            self.statusText.setText(str(error))

    def snapEvent(self) :
        if len(self.imageDict["image"])<=0 : 
            self.statusText.setText("no image is available")
            return
        self.snapDisplay.newImage(self.imageDict)
        self.snapDisplay.display()

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
                self.statusText.setText(str(error))
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
            self.statusText.setText(str(error))
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
            self.imageDict["dtype"] = data.dtype
            self.dtypeText.setText(str(self.imageDict["dtype"]))
        try:
            if codecNameLength != 0 : 
                data = self.decompress(data,codec,compressed,uncompressed)
            self.dataToImage(data,dimArray)
            self.dynamicDisplay.newImage(self.imageDict)
            self.dynamicDisplay.display()
        except Exception as error:
            self.statusText.setText(str(error))
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
        if typevalue== 1 : dtype = "int8"; elementsize =int(1)
        elif typevalue== 5 : dtype = "uint8"; elementsize =int(1)
        elif typevalue== 2 : dtype = "int16"; elementsize =int(2)
        elif typevalue== 6 : dtype = "uint16"; elementsize =int(2)
        elif typevalue== 3 : dtype = "int32"; elementsize =int(4)
        elif typevalue== 7 : dtype = "uint32"; elementsize =int(4)
        elif typevalue== 4 : dtype = "int64"; elementsize =int(8)
        elif typevalue== 8 : dtype = "uint64"; elementsize =int(8)
        elif typevalue== 9 : dtype = "float32"; elementsize =int(4)
        elif typevalue== 10 : dtype = "float64"; elementsize =int(8)
        else : raise Exception('decompress mapIntToType failed')
        if codecName=='blosc':
            lib = self.findLibrary.find(codecName)
        elif codecName=='jpeg' :
            lib = self.findLibrary.find('decompressJPEG')
        elif codecName=='lz4' or codecName=='bslz4' :
            lib = self.findLibrary.find('bitshuffle')
        else : lib = None
        if lib==None : raise Exception('shared library ' +codecName + ' not found')
        self.imageDict["dtype"] = dtype
        self.dtypeText.setText(str(self.imageDict["dtype"]))
        inarray = bytearray(data)
        in_char_array = ctypes.c_ubyte * compressed
        out_char_array = ctypes.c_ubyte * uncompressed
        outarray = bytearray(uncompressed)
        if codecName=='blosc' : 
            lib.blosc_decompress(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),uncompressed)
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=dtype)
        elif codecName=='lz4' :
            lib.LZ4_decompress_fast(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),uncompressed)
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=dtype)
        elif codecName=='bslz4' :
            lib.bshuf_decompress_lz4(
                 in_char_array.from_buffer(inarray),
                 out_char_array.from_buffer(outarray),int(uncompressed/elementsize),
                 elementsize,int(0))
            data = np.array(outarray)
            data = np.frombuffer(data,dtype=dtype)
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
        dtype = data.dtype
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
        if dtype!=self.imageDict["dtype"] :
            self.imageDict["dtype"] = dtype
            self.dtypeText.setText(str(self.imageDict["dtype"]))
        if ny <self.minsize or nx<self.minsize :
            raise Exception('ny <',self.minsize,' or nx<',self.minsize)
        if nx!=self.imageDict["nx"] :
            self.imageDict["nx"] = nx
            self.nxText.setText(str(self.imageDict["nx"]))
        if ny!=self.imageDict["ny"] :
            self.imageDict["ny"] = ny
            self.nyText.setText(str(self.imageDict["ny"]))
        if nz!=self.imageDict["nz"] :
            self.imageDict["nz"] = nz
            self.nzText.setText(str(self.imageDict["nz"]))
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
        self.imageDict["image"] = image

