# NTNDA_ZoomImage_Display.py
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

from PyQt5.QtWidgets import QWidget,QLabel,QLineEdit
from PyQt5.QtWidgets import QPushButton,QHBoxLayout,QGridLayout

from NTNDA_Image_Display import NTNDA_Image_Display

import numpy as np
class Image_Display(RawImageWidget) :
    def __init__(self,parent=None, **kargs):
        RawImageWidget.__init__(self, parent=parent,scaled=True)

    def display(self,image,pixelLevels) :
        self.setImage(image,levels=pixelLevels)
        self.show()
        

class NTNDA_ZoomImage_Display(NTNDA_Image_Display,QWidget) :
    '''
    Displaying an zoom image
    The methods are call by NTNDA_Viewer.
    '''
    def __init__(self, name,left,top,parent=None, **kargs):
        NTNDA_Image_Display.__init__(self, name,left,top,parent=None, **kargs)
        QWidget.__init__(self, parent=parent)
        self.imageDisplay = Image_Display()
        self.xlow = 0
        self.ylow = 0
        self.numx = 0
        self.numy = 0
# control row
        controlLabel = QLabel('(xlow,ylow,nx.ny)')
        self.controlText = QLineEdit()
        self.controlText.setEnabled(True)
        self.controlText.setFixedWidth(400)
        self.controlText.editingFinished.connect(self.controlTextEvent)
        self.resetButton = QPushButton('reset')
        self.resetButton.setEnabled(True)
        self.resetButton.clicked.connect(self.resetEvent)
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(controlLabel)
        box.addWidget(self.controlText)
        box.addWidget(self.resetButton)
        wid =  QWidget()
        wid.setLayout(box)
        self.controlRow = wid
# image row
        box = QHBoxLayout()
        box.setContentsMargins(0,0,0,0);
        box.addWidget(self.imageDisplay)
        wid =  QWidget()
        wid.setLayout(box)
        wid.setFixedHeight(600)
        wid.setFixedWidth(600)
        self.imageRow = wid
# initialize
        layout = QGridLayout()
        layout.setVerticalSpacing(0);
        layout.addWidget(self.controlRow,0,0)
        layout.addWidget(self.imageRow,1,0)
        self.setLayout(layout)
        value = '{:>40}'.format(name) + ' control       '
        self.setWindowTitle(value)

    def resetEvent(self) :
        control = '(0,0,' + str(self.nx) + ',' + str(self.ny) + ')'
        self.controlText.setText(control)
        self.imageDisplay.display(self.image,self.pixelLevels)

    def controlTextEvent(self) :
        try :
            text = self.controlText.text()
            ind = text.find('(')
            if ind<0 : raise Exception('does not start with (')
            text = text[(ind+1):]
            ind = text.find(')')
            if ind<0 : raise Exception('does not end with )')
            text = text[:-1]
            split = text.split(',')
            xlow = int(split[0])
            ylow = int(split[1])
            numx = int(split[2])
            numy = int(split[3])
        except Exception as error:
            self.controlText.setText('error:' + repr(error))
        reset = False
        if xlow>(self.nx-16) : xlow = self.nx - 16; reset = True
        if ylow>(self.ny-16) : ylow = self.ny - 16; reset = True
        if numx>(self.nx-xlow) : numx = self.nx - xlow; reset = True
        if numy>(self.ny-ylow) : numy = self.ny - ylow; reset = True
        self.xlow = xlow
        self.ylow = ylow
        self.numx = numx
        self.numy = numy
        if reset :
            control = '(' + str(self.xlow) +',' + str(self.ylow) \
                    + ',' +str(self.numx) + ',' + str(self.numy) + ')'
            self.controlText.setText(control)
        self.displayZoom()

    def displayZoom(self) :
        if self.nz==1 :
            image = np.empty((self.numx,self.numy),dtype=self.image.dtype)
            for indx in range(0,self.numx) :
                for indy in range(0,self.numy) :
                    image[indx][indy] = self.image[indx+self.xlow][indy+self.ylow]
        elif self.nz==3 :
            image = np.empty((self.numx,self.numy,3),dtype=self.image.dtype)
            for indx in range(0,self.numx) :
                for indy in range(0,self.numy) :
                    for indz in range(0,3) :
                        image[indx][indy][indz] = self.image[indx+self.xlow][indy+self.ylow][indz]
        else : raise Exception('ndim not 2 or 3')
        self.imageDisplay.display(image,self.pixelLevels)
    def display(self) :
        self.image = self.arg[0]
        self.nx = self.arg[3]
        self.ny = self.arg[4]
        self.nz = self.arg[5]
        self.resetEvent()
        self.imageDisplay.display(self.image,self.pixelLevels)
        self.show()
        return 0
