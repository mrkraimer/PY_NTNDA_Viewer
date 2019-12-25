#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *
from PyQt5.QtWidgets import QApplication,QWidget,QDialog,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QLayout,QHBoxLayout,QVBoxLayout,QLayoutItem,QGridLayout,QPlainTextEdit
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

class ImageDisplay(RawImageWidget):
    def __init__(self, parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent)
        self.title = 'ImageDisplay'
        self.left = 1
        self.top = 240
        self.maxsize = 800
        self.minsize = 16
        self.nx = 0
        self.ny = 0
        self.nz = 0
        self.width = self.maxsize
        self.height = self.maxsize
        self.data = None
        self.datatype = 'none'
        self.channel = None
        self.nxText = QLineEdit()
        self.nxText.setFixedWidth(50)
        self.nyText = QLineEdit()
        self.nyText.setFixedWidth(50)
        self.nzText = QLineEdit()
        self.nzText.setFixedWidth(50)
        self.maxsizeText = QLineEdit()
        self.maxsizeText.setFixedWidth(50)
        self.maxsizeText.setText(str(self.maxsize))
        self.widthText = QLineEdit()
        self.widthText.setFixedWidth(50)
        self.widthText.setText(str(self.width))
        self.heightText = QLineEdit()
        self.heightText.setFixedWidth(50)
        self.heightText.setText(str(self.height))
        self.imageRateText = QLineEdit()
        self.nxText.setEnabled(False)
        self.nyText.setEnabled(False)
        self.nzText.setEnabled(False)
        self.widthText.setEnabled(False)
        self.heightText.setEnabled(False)
        self.imageRateText.setEnabled(False)
        self.lasttime = time.time() -2
        self.nImages = 0
        self.initUI()

    def createRowWidget(self) :
        box = QHBoxLayout()
        maxsizeLabel = QLabel("maxsize:")
        maxsizeLabel.setBuddy(self.maxsizeText)
        box.addWidget(maxsizeLabel)
        box.addWidget(self.maxsizeText)
        nxLabel = QLabel("nx=")
        nxLabel.setFixedWidth(20)
        nxLabel.setBuddy(self.nxText)
        self.nxText.setText('0')
        box.addWidget(nxLabel)
        box.addWidget(self.nxText)
        nyLabel = QLabel("ny=")
        nyLabel.setFixedWidth(20)
        nyLabel.setBuddy(self.nyText)
        self.nyText.setText('0')
        box.addWidget(nyLabel)
        box.addWidget(self.nyText)
        nzLabel = QLabel("nz=")
        nzLabel.setFixedWidth(20)
        nzLabel.setBuddy(self.nzText)
        self.nzText.setText('0')
        box.addWidget(nzLabel)
        box.addWidget(self.nzText)

        widthLabel = QLabel("width=")
        widthLabel.setFixedWidth(40)
        widthLabel.setBuddy(self.widthText)
        box.addWidget(widthLabel)
        box.addWidget(self.widthText)
        heightLabel = QLabel("height=")
        heightLabel.setFixedWidth(40)
        heightLabel.setBuddy(self.heightText)
        box.addWidget(heightLabel)
        box.addWidget(self.heightText)


        imageRateLabel = QLabel("imageRate=")
        imageRateLabel.setBuddy(self.imageRateText)
        box.addWidget(imageRateLabel)
        box.addWidget(self.imageRateText)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(40)
        return wid
    
    def maxsizeEvent(self) :
        print('maxsize event',flush=True)
        self.maxsize = int(self.maxsizeText.text())

    def initUI(self):
        self.maxsizeText.editingFinished.connect(self.maxsizeEvent)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()    

    def getMaxsize(self) :
        return self.maxsize

    def setMaxsize(self,maxsize) :
        self.maxsize = maxsize

    def newImage(self,arg):
        value = None
        try:
            value = arg['value'][0]
        except Exception as error:
            self.title = repr(error)
            return
        if len(value) != 1 :
            self.title = 'value length not 1'
            return
        dimArray = None
        try:
            dimArray = arg['dimension']
        except Exception as error:
            self.title = repr(error)
            return
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
        if (height!=self.height) or (width!=self.width) :
            print("resize")
            self.width = width
            self.height = height
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.widthText.setText(str(self.width))
            self.heightText.setText(str(self.height))
        self.setImage(image)
        self.nImages = self.nImages + 1
        self.timenow = time.time()
        timediff = self.timenow - self.lasttime
        if(timediff<1) : return        
        images = self.nImages/timediff
        imgfmt = '{0:.2f}'.format(images)
        text =  imgfmt + "/sec"
        self.imageRateText.setText(text)
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
        self.statusText = QLineEdit()
        self.initUI()

    def connectEvent(self) :
        print('connect event',flush=True)
        self.connect()
        self.connectButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.disconnectButton.setEnabled(True)

    def disconnectEvent(self) :
        print('disconnect event',flush=True)
        self.disconnect()
        self.connectButton.setEnabled(True)
        self.startButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)

    def startEvent(self) :
        print('start event',flush=True)
        self.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.disconnectButton.setEnabled(False)

    def stopEvent(self) :
        print('stop event',flush=True)
        self.stop()
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.disconnectButton.setEnabled(True)

    def channelNameEvent(self) :
        print('channelName event',flush=True)
        self.channelName = self.channelNameText.text()

    def mycallback(self,arg):
        try:
            self.imageDisplay.newImage(arg)
        except Exception as error:
            self.imageDisplay.title = repr(error)
        

    def setChannelName(self,channelName) :
        self.channelName = channelName
        self.channelNameText.setText(self.channelName)

    def connect(self) :
        self.channel = Channel(self.channelName)
        self.channel.subscribe('mycallback', self.mycallback)

    def start(self) :
        self.channel.startMonitor('field()')

    def disconnect(self) :
        self.channel = None

    def stop(self) :
        self.channel.stopMonitor()

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

    def initUI(self):
        self.connectButton.clicked.connect(self.connectEvent)
        self.disconnectButton.clicked.connect(self.disconnectEvent)
        self.startButton.clicked.connect(self.startEvent)
        self.stopButton.clicked.connect(self.stopEvent)
        self.channelNameText.editingFinished.connect(self.channelNameEvent)
        self.setGeometry(1, 1, 900, 40)
        self.createFirstRow()
        layout = QGridLayout()
        layout.addWidget(self.firstRow,0,0)
        self.imageDisplay = ImageDisplay()
        layout.addWidget(self.imageDisplay.createRowWidget(),1,0)
        self.statusText.setText('nothing done so far')
        layout.addWidget(self.statusText,2,0)
        self.setLayout(layout)
        self.channelNameText.setText('')
        self.show()

if __name__ == '__main__':
    nargs = len(sys.argv)
    if nargs<2 :
        print("args: channelName")
        exit()
    channelName = sys.argv[1]
    app = QApplication(sys.argv)
    viewer = PY_NTNDA_Viewer()
    viewer.setChannelName(channelName)
    sys.exit(app.exec_())

