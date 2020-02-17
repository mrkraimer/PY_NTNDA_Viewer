# NTNDA_Image_Display.py

class NTNDA_Image_Display(object) :
    '''
    Base class for displaying an image provided by NTNDA_Viewer
    The methods are call by NTNDA_Viewer.
    '''
    def __init__(self, name,left,top,parent=None, **kargs):
        self.name = name
        self.left = left
        self.top = top
        self.maxsize = 800
        self.width = self.maxsize
        self.height = self.maxsize
        self.ignoreClose = True
        self.pixelLevels = (0,0)
        self.okToClose = False
        self.isHidden = True
        self.arg = None

    def closeEvent(self, event) :
        if self.ignoreClose :
            event.ignore()
            self.isHidden = True
            self.hide()

    def setPixelLevels(self,pixelLevels) :
        self.pixelLevels = pixelLevels

    def newImage(self,arg):
        self.arg = arg

    def display(self) :
        pass
