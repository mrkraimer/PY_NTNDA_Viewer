# NTNDA_RawImage_Display.py
from pyqtgraph.widgets.RawImageWidget import RawImageWidget

from NTNDA_Image_Display import NTNDA_Image_Display

class NTNDA_RawImage_Display(NTNDA_Image_Display,RawImageWidget) :
    '''
    Displaying an image via RawImageWidget
    The methods are call by NTNDA_Viewer.
    '''
    def __init__(self, name,left,top,parent=None, **kargs):
        NTNDA_Image_Display.__init__(self, name,left,top,parent=None, **kargs)
        RawImageWidget.__init__(self, parent=parent,scaled=True)
        self.setObjectName(self.name)
        self.setWindowTitle(self.name)

    def display(self) :
        image = self.arg[0]
        width = self.arg[1]
        height = self.arg[2]
        if self.isHidden or width!= self.width or height!=self.height :
            self.width = width
            self.height = height
            self.isHidden = False
            self.setGeometry(self.left, self.top, self.width, self.height)
            self.show()
        self.setImage(image,levels=self.pixelLevels)
        return 0
