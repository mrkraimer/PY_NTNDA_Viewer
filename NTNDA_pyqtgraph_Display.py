# NTNDA_pyqtgraph_Display.py

import pyqtgraph as pg
from NTNDA_Image_Display import NTNDA_Image_Display

class NTNDA_pyqtgraph_Display(NTNDA_Image_Display) :
    '''
    Displaying an pyqtgraph image
    The methods are call by NTNDA_Viewer.
    '''
    def __init__(self, name,left,top,parent=None, **kargs):
        NTNDA_Image_Display.__init__(self, name,left,top,parent=None, **kargs)
        self.name = name
        self.left = left
        self.top = top

    def display(self) :
        img = self.arg[0]
        pg.image(img,title=self.name)
