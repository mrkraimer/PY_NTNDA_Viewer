#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *

from threading import Event, Thread

from PyQt5 import QtCore,  QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QLineEdit, QLabel
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QImage, QPixmap, qRgb

class ImageDisplay(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'ImageDisplay'
        self.left = 1
        self.top = 1
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.label = QLabel(self)
        self.show()    

    def newImage(self,pixmap):
        width = pixmap.width()*.75
        height = pixmap.height()*.75
        if (height!=self.height) or (width!=self.width) :
            time.sleep(.1)
            print("resize")
            self.height = height
            self.width = width
            self.label.resize(width,height)
            self.resize(width,height)
            time.sleep(.1)
        self.label.setPixmap(pixmap)
        pixmap = None

gray_color_table = [qRgb(i, i, i) for i in range(256)]

def create2dPixmap(value,dimArray) :
    ny = dimArray[0]["size"]
    nx = dimArray[1]["size"]
    element = None
    for x in value :
        element = x
    if element == None : 
       raise Exception('value is not numpyarray')
    data = value[element]
    datatype = data.dtype
    image = data.reshape(nx,ny)
    if image.dtype != np.uint8:
       raise Exception('value element type is not uint8')
    qim = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Indexed8)
    qim.setColorTable(gray_color_table)
    pixmap = QPixmap(qim)
    return pixmap


def create3dPixmap(value,dimArray) :
    if dimArray[0]["size"]==3 :
        nx = dimArray[1]["size"]
        ny = dimArray[2]["size"]
        nz = dimArray[0]["size"]
    elif dimArray[1]["size"]==3 :
        nx = dimArray[0]["size"]
        ny = dimArray[2]["size"]
        nz = dimArray[1]["size"]
    elif dimArray[2]["size"]==3 :
        nx = dimArray[0]["size"]
        ny = dimArray[1]["size"]
        nz = dimArray[2]["size"]
    else  :  raise Exception('no dim = 3')
    element = None
    for x in value :
        element = x
    if element == None : 
       raise Exception('value is not numpyarray')
    data = value[element]
    datatype = data.dtype
    image = data.reshape(ny,nx,nz)
    if image.dtype != np.uint8:
       raise Exception('value element type is not uint8')
    qim = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888)
    pixmap = QPixmap(qim)
    return pixmap

def createPixmap(value,dimArray) :
    ndim = len(dimArray)
    if ndim ==2 :
        return create2dPixmap(value,dimArray)
    if ndim ==3 :
        return create3dPixmap(value,dimArray)
    raise Exception('ndim not 2 or 3')

def mycallback(arg):
    global lasttime
    global nImages
    global imageThread
    global app
    global display
    global imageDisplay
    time.sleep(.001)
    value = None
    try:
        value = arg['value'][0]
    except Exception as error:
        imageDisplay.setWindowTitle(repr(error))
        return
    if len(value) != 1 :
        imageDisplay.setWindowTitle('value length not 1')
        return
    dimArray = None
    try:
        dimArray = arg['dimension']
    except Exception as error:
        imageDisplay.setWindowTitle(repr(error))
        return
    pixmap = None
    try:
        pixmap = createPixmap(value,dimArray)
    except Exception as error :
        imageDisplay.setWindowTitle(repr(error))
        return
    try:
        imageDisplay.newImage(pixmap)
    except Exception as error:
        imageDisplay.setWindowTitle(repr(error))
        return
    time.sleep(.002)
    nImages = nImages + 1
    timenow = time.time()
    timediff = timenow - lasttime
    if(timediff<1) : return    
    images = nImages/timediff
    imgfmt = '{0:.2f}'.format(images)
    text = "images/sec " + imgfmt
    imageDisplay.setWindowTitle(text)
    lasttime = timenow
    nSinceLastReport = 0
    nImages = 0


if __name__ == '__main__':
    nargs = len(sys.argv)
    if nargs<2 :
        print("args: channelName")
        exit()
    channelName = sys.argv[1]
    app = QApplication(sys.argv)
    imageDisplay = ImageDisplay()
    
    nSinceLastReport = 0
    nImages = 0;
    lasttime = time.time() -2
    channel = Channel(channelName)
    channel.subscribe('mycallback', mycallback)
    channel.startMonitor('field()')
    sys.exit(app.exec_())

