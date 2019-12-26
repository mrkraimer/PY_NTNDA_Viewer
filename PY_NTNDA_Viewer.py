#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *
from PyQt5.QtWidgets import QApplication,QWidget,QDialog,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QLayout,QHBoxLayout,QVBoxLayout,QLayoutItem,QGridLayout,QPlainTextEdit
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

class ImageDisplay(RawImageWidget):
    def __init__(self,viewer, parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent)
        self.viewer = viewer
        self.title = 'ImageDisplay'
        self.left = 1
        self.top = 250
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
        self.lasttime = time.time() -2
        self.nImages = 0
        self.okToClose = False
        self.isShow = False
        self.viewer.maxsizeText.editingFinished.connect(self.maxsizeEvent)

    def closeEvent(self, event) :
        if not self.okToClose : event.ignore()

    def maxsizeEvent(self) :
        print('maxsize event',flush=True)
        self.maxsize = int(self.viewer.maxsizeText.text())

    def getMaxsize(self) :
        return self.maxsize

    def setMaxsize(self,maxsize) :
        self.maxsize = maxsize

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
            if str(data.dtype)!=self.datatype :
                self.datatype = str(data.dtype)
                print("datatype=",self.datatype,flush=True)
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
            data = value[element]
            if str(data.dtype)!=self.datatype :
                self.datatype = str(data.dtype)
                print("datatype=",self.datatype,flush=True)
            image = data.reshape(ny,nx,nz)
        else :
            raise Exception('ndim not 2 or 3')
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
            print("resize")
            self.width = width
            self.height = height
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.viewer.widthText.setText(str(self.width))
            self.viewer.heightText.setText(str(self.height))
        if not self.isShow :
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.viewer.widthText.setText(str(self.width))
            self.viewer.heightText.setText(str(self.height))
            self.isShow = True
            self.show()
        self.setImage(image)
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
        self.initUI()
    def closeEvent(self, event) :
        if not self.channel==None : 
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

    def disconnectEvent(self) :
        self.disconnect()
        self.connectButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)

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

    def mycallback(self,arg):
        if self.imageDisplay==None :
            self.imageDisplay = ImageDisplay(self)
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
        try:
            self.imageDisplay.newImage(value,dimArray)
        except Exception as error:
            self.statusText.setText(repr(error))
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
    def initUI(self):
        self.connectButton.clicked.connect(self.connectEvent)
        self.disconnectButton.clicked.connect(self.disconnectEvent)
        self.startButton.clicked.connect(self.startEvent)
        self.stopButton.clicked.connect(self.stopEvent)
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        self.setGeometry(1, 1, 900, 40)
        self.createFirstRow()
        self.createSecondRow()
        layout = QGridLayout()
        layout.addWidget(self.firstRow,0,0)
        layout.addWidget(self.secondRow,1,0)
        self.statusText.setText('nothing done so far')
        layout.addWidget(self.statusText,2,0)
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

