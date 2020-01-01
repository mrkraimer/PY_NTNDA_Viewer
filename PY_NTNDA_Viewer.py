#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *
import threading
from PyQt5.QtWidgets import QApplication,QWidget,QDialog,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QLayout,QHBoxLayout,QVBoxLayout,QLayoutItem,QGridLayout,QPlainTextEdit
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

from ast import literal_eval as make_tuple

class ImageDisplay(RawImageWidget):
    def __init__(self,viewer, parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent)
        self.viewer = viewer
        self.title = 'ImageDisplay'
        self.left = 1
        self.top = 300
        self.maxsize = 768
        self.viewer.maxsizeText.setText(str(self.maxsize))
        self.minsize = 16
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.width = self.maxsize
        self.height = self.maxsize
        self.data = None
        self.datatype = 'none'
        self.pixelLevels = (0,0)
        self.lasttime = time.time() -2
        self.nImages = 0
        self.okToClose = False
        self.firstCallback = True

    def closeEvent(self, event) :
        if not self.okToClose : event.ignore()

    def setMaxsize(self,maxsize) :
        self.maxsize = maxsize

    def setPixelLevels(self,pixelLevels) :
        try :
           temp = make_tuple(pixelLevels)
           self.pixelLevels = temp
        except Exception as error:
           self.viewer.statusText.setText("setPixelLevels error=" + repr(error))
        
    def newImage(self,value,dimArray):
        image = None
        ny = 0
        nx = 0
        nz = 1
        ndim = len(dimArray)
        if ndim ==2 :
            ny = dimArray[1]["size"]
            nx = dimArray[0]["size"]
            element = None
            for x in value :
                element = x
            if element == None : 
                raise Exception('value is not numpyarray')
            data = value[element]
            datatype = str(data.dtype)
            image = data.reshape(nx,ny)
        elif ndim ==3 :
            if dimArray[0]["size"]==3 :
                nz = dimArray[0]["size"]
                nx = dimArray[1]["size"]
                ny = dimArray[2]["size"]
            elif dimArray[1]["size"]==3 :
                nz = dimArray[1]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[2]["size"]
            elif dimArray[2]["size"]==3 :
                nz = dimArray[2]["size"]
                nx = dimArray[0]["size"]
                ny = dimArray[1]["size"]
            else  :  raise Exception('no dim = 3')
            element = None
            for x in value :
                element = x
            if element == None : 
                raise Exception('value is not numpyarray')
                return
            data = value[element]
            datatype = str(data.dtype)
            image = data.reshape(ny,nx,nz)
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
                self.pixelLevels = (int(0),int(2147483648))
            elif datatype==str("int64") :
                self.pixelLevels = (int(-9223372036854775808),int(9223372036854775807))
            elif datatype==str("uint64") :
                self.pixelLevels = (int(0),int(18446744073709551615))
            elif datatype==str("float32") :
                self.pixelLevels = (float(0.0),float(3000.0))
            elif datatype==str("float64") :
                raise Exception('float64 is not supported')
                return
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
        if (height!=self.height) or (width!=self.width) :
            self.width = width
            self.height = height
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.viewer.widthText.setText(str(self.width))
            self.viewer.heightText.setText(str(self.height))
        if self.firstCallback :
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.viewer.widthText.setText(str(self.width))
            self.viewer.heightText.setText(str(self.height))
            self.firstCallback = False
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

class PY_NTNDA_Viewer(QDialog) :
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.event = threading.Event()
        self.event.set()
        self.setWindowTitle("PY_NTNDA_Viewer")
        self.channelNameText = QLineEdit()
        self.channelNameText.setEnabled(True)
        self.channelName = ''
        self.channel = None
        self.connectButton = QPushButton('connect')
        self.connectButton.setEnabled(True)
        self.disconnectButton = QPushButton('disconnect')
        self.disconnectButton.setEnabled(False)
        self.startButton = QPushButton('start')
        self.startButton.setEnabled(False)
        self.stopButton = QPushButton('stop')
        self.stopButton.setEnabled(False)
        self.isConnected = False

        self.imageDisplay = None
        self.statusText = QLineEdit()
        self.nxText = QLabel()
        self.nxText.setFixedWidth(50)
        self.nyText = QLabel()
        self.nyText.setFixedWidth(50)
        self.nzText = QLabel()
        self.nzText.setFixedWidth(50)
        self.maxsizeText = QLineEdit()
        self.maxsizeText.setFixedWidth(50)
        self.widthText = QLabel()
        self.widthText.setFixedWidth(50)
        self.heightText = QLabel()
        self.heightText.setFixedWidth(50)
        self.imageRateText = QLabel()
        self.dtypeText = QLabel()
        self.pixelLevelsText = QLineEdit()
        self.pixelLevelsText.setEnabled(True)
        self.initUI()
    def closeEvent(self, event) :
        if self.isConnected : 
            event.ignore()
            return
        if self.imageDisplay!=None :
            self.imageDisplay.okToClose = True
            self.imageDisplay.close()
        
    def connectEvent(self) :
        self.connect()
        self.connectButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.disconnectButton.setEnabled(True)
        self.isConnected = True

    def disconnectEvent(self) :
        self.disconnect()
        self.connectButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.isConnected = False

    def startEvent(self) :
        self.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)

    def stopEvent(self) :
        self.stop()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)

    def channelNameEvent(self) :
        self.setChannelName(self.channelNameText.text())

    def maxsizeEvent(self) :
        maxsize = int(self.maxsizeText.text())
        self.event.wait()
        try:
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
        if len(value) != 1 :
            self.statusText.setText('value length not 1')
            return
        dimArray = None
        try:
            dimArray = arg['dimension']
        except Exception as error:
            self.statusText.setText(repr(error))
            return
        callAgain = True
        self.event.wait()
        try:
            self.imageDisplay.newImage(value,dimArray)
        except Exception as error:
            self.statusText.setText(repr(error))
        self.event.set()
    def setChannelName(self,channelName) :
        self.channelName = channelName
        self.channelNameText.setText(self.channelName)

    def connect(self) :
        self.channel = Channel(self.channelName)
        self.channel.subscribe('mycallback', self.mycallback)
        self.statusText.setText('connecting')
    def start(self) :
        if self.imageDisplay==None :
            self.imageDisplay = ImageDisplay(self)
        self.channel.startMonitor('field()')
        self.statusText.setText('starting')
    def disconnect(self) :
        self.channel = None
        self.statusText.setText('disconnecting')
        if self.imageDisplay!=None :
            self.imageDisplay.okToClose = True
            self.imageDisplay.close()
            self.imageDisplay = None
    def stop(self) :
        self.channel.stopMonitor()
        self.statusText.setText('stoping')
    def createFirstRow(self) :
        box = QHBoxLayout()
        box.addWidget(self.connectButton)
        box.addWidget(self.disconnectButton)
        box.addWidget(self.startButton)
        box.addWidget(self.stopButton)
        channelNameLabel = QLabel("channelName:")
        channelNameLabel.setBuddy(self.channelNameText)
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
        dtypeLabel.setFixedWidth(60)
        box.addWidget(dtypeLabel)
        box.addWidget(self.dtypeText)
        self.dtypeText.setFixedWidth(60)
        pixelLevelsLabel = QLabel("pixel levels:")
        pixelLevelsLabel.setFixedWidth(80)
        box.addWidget(pixelLevelsLabel)
        box.addWidget(self.pixelLevelsText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        self.thirdRow = wid

    def initUI(self):
        self.connectButton.clicked.connect(self.connectEvent)
        self.disconnectButton.clicked.connect(self.disconnectEvent)
        self.startButton.clicked.connect(self.startEvent)
        self.stopButton.clicked.connect(self.stopEvent)
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        self.maxsizeText.editingFinished.connect(self.maxsizeEvent)
        self.pixelLevelsText.editingFinished.connect(self.pixelLevelsEvent)
        self.setGeometry(1, 1, 900, 40)
        self.createFirstRow()
        self.createSecondRow()
        self.createThirdRow()
        layout = QGridLayout()
        layout.addWidget(self.firstRow,0,0)
        layout.addWidget(self.secondRow,1,0)
        layout.addWidget(self.thirdRow,2,0)
        self.statusText.setText('nothing done so far')
        layout.addWidget(self.statusText,3,0)
        self.setLayout(layout)
        self.channelNameText.setText('')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = PY_NTNDA_Viewer()
    nargs = len(sys.argv)
    if nargs>=2 :
        channelName = sys.argv[1]
        viewer.setChannelName(channelName)
    sys.exit(app.exec_())

