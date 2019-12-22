#!/usr/bin/env python

import sys,time
import numpy as np
from pvaccess import *

from PyQt5.QtWidgets import QApplication
from pyqtgraph.widgets.RawImageWidget import RawImageWidget


class ImageDisplay(RawImageWidget):
    def __init__(self, parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent)
        self.title = 'ImageDisplay'
        self.left = 1
        self.top = 1
        self.maxsize = 800
        self.minsize = 16
        self.width = self.maxsize
        self.height = self.maxsize
        self.data = None
        self.datatype = 'none'
        self.initUI()
    
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()    

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
            print("self.width=",self.width," self.height=",self.height,flush=True)
        self.setImage(image)

def mycallback(arg):
    global lasttime
    global nImages
    global imageDisplay
    try:
        imageDisplay.newImage(arg)
    except Exception as error:
        imageDisplay.title = repr(error)
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

