
import logging
logger = logging.getLogger(__name__)


import sys
import os
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtOpenGL

from spimagine.floatslider import FloatSlider

import numpy as np


from gui_utils import createStandardCheckbox,createStandardButton


import spimagine


def absPath(myPath):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        return os.path.join(base_path, os.path.basename(myPath))
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, myPath)


checkBoxStyleStr = """
    QCheckBox::indicator:checked {
    background:black;
    border-image: url(%s);}
    QCheckBox::indicator:unchecked {
    background:black;
    border-image: url(%s);}
    """

def createImgCheckBox(fName_active,fName_inactive):
    checkBox = QtGui.QCheckBox()
    checkBox.setStyleSheet(
            checkBoxStyleStr%(absPath(fName_active),absPath(fName_inactive)))
    return checkBox



class VolumeSettingsPanel(QtGui.QWidget):
    _stackUnitsChanged = QtCore.pyqtSignal(float,float,float)
    _boundsChanged =  QtCore.pyqtSignal(float,float,float,float,float,float)
    _alphaPowChanged = QtCore.pyqtSignal(float)
    _rgbColorChanged = QtCore.pyqtSignal(float, float,float)
    
    def __init__(self):
        super(QtGui.QWidget,self).__init__()

        self.resize(50, 300)
        self.initUI()


    def initUI(self):



        vbox = QtGui.QVBoxLayout()

        vbox.addWidget(QtGui.QLabel("Stack units",alignment = QtCore.Qt.AlignCenter))
        # The stack units line edits
        stackLabels = ["x","y","z"]


        self.stackEdits = []
        for lab in stackLabels:
            hbox = QtGui.QHBoxLayout()
            edit = QtGui.QLineEdit("1.0")
            edit.setValidator(QtGui.QDoubleValidator(bottom=1e-10))
            edit.returnPressed.connect(self.stackUnitsChanged)
            hbox.addWidget(QtGui.QLabel(lab))
            hbox.addWidget(edit)
            vbox.addLayout(hbox)
            self.stackEdits.append(edit)


        vbox.addWidget(QtGui.QLabel("Borders",alignment = QtCore.Qt.AlignCenter))

        gridBox = QtGui.QGridLayout()
        self.sliderBounds = [QtGui.QSlider(QtCore.Qt.Horizontal) for _ in range(6)]
        for i,s in enumerate(self.sliderBounds):
            s.setTickPosition(QtGui.QSlider.TicksBothSides)
            s.setRange(-100,100)
            s.setTickInterval(1)
            s.setFocusPolicy(QtCore.Qt.ClickFocus)
            s.setTracking(True)
            s.setValue(-100+200*(i%2))
            s.valueChanged.connect(self.boundsChanged)
            s.setStyleSheet("height: 18px; border = 0px;")

            gridBox.addWidget(s,i,1)


        vbox.addLayout(gridBox)
            
        line =  QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)

        vbox.addWidget(line)
        vbox.addWidget(QtGui.QLabel("Display",alignment = QtCore.Qt.AlignCenter))

        # the perspective/box checkboxes
        self.checkProj = createStandardCheckbox(self,absPath("images/rays_persp.png"),
                                                    absPath("images/rays_ortho.png"), tooltip="projection")

        self.checkBox = createStandardCheckbox(self,absPath("images/wire_cube.png"),
                                                    absPath("images/wire_cube_incative.png"),
                                                    tooltip="toggle box")

        self.butColor = createStandardButton(self,absPath("images/icon_colors.png"),
                                             method = self.onButtonColor,
                                                    tooltip="color")

        gridBox = QtGui.QGridLayout()

        gridBox.addWidget(QtGui.QLabel("projection:\t"),1,0)
        gridBox.addWidget(self.checkProj,1,1)

        gridBox.addWidget(QtGui.QLabel("bounding box:\t"),2,0)
        gridBox.addWidget(self.checkBox,2,1)

        gridBox.addWidget(QtGui.QLabel("colormap:\t"),3,0)

        self.colorCombo = QtGui.QComboBox()

        self.colormaps = list(spimagine.__COLORMAPDICT__.keys())

        self.colorCombo.setIconSize(QtCore.QSize(100,20))

        for s in self.colormaps:
            self.colorCombo.addItem(QtGui.QIcon(absPath("colormaps/cmap_%s.png"%s)),"")

        gridBox.addWidget(self.colorCombo,3,1)

        gridBox.addWidget(self.butColor,4,0)


        self.sliderAlphaPow = FloatSlider(QtCore.Qt.Horizontal)
        self.sliderAlphaPow.setRange(0,1.,100)
        self.sliderAlphaPow.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.sliderAlphaPow.setTracking(True)
        self.sliderAlphaPow.setValue(1.)

        gridBox.addWidget(QtGui.QLabel("opacity transfer:\t"),5,0)
        gridBox.addWidget(self.sliderAlphaPow,5,1)


        self.sliderEyeProj = FloatSlider(QtCore.Qt.Horizontal)
        self.sliderEyeProj.setRange(-0.005,0.005,100)
        self.sliderEyeProj.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.sliderEyeProj.setTracking(True)
        self.sliderEyeProj.setValue(0)
        gridBox.addWidget(QtGui.QLabel("eye proj:\t"))
        gridBox.addWidget(self.sliderEyeProj)

        self.sliderEyeCam = FloatSlider(QtCore.Qt.Horizontal)
        self.sliderEyeCam.setRange(-0.06,0.06,100)
        self.sliderEyeCam.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.sliderEyeCam.setTracking(True)
        self.sliderEyeCam.setValue(0)

        gridBox.addWidget(QtGui.QLabel("eye cam:\t"))
        gridBox.addWidget(self.sliderEyeCam)

        vbox.addLayout(gridBox)

        # vbox.addStretch()
        line =  QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)

        vbox.addWidget(line)

        #################

        line =  QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        vbox.addWidget(line)

        self.dimensionLabel = QtGui.QLabel("Dimensions:",alignment = QtCore.Qt.AlignLeft)
        vbox.addWidget(self.dimensionLabel)

        self.statsLabel = QtGui.QLabel("Max: Min: Mean:",alignment = QtCore.Qt.AlignLeft)
        vbox.addWidget(self.statsLabel)

        self.setStyleSheet("""
        QFrame,QLabel,QLineEdit {
        color: white;
        }
        """)
        self.colorCombo.setStyleSheet("background-color:none;")

        vbox.addStretch()

        self.setLayout(vbox)



    def onButtonColor(self):
        col = QtGui.QColorDialog.getColor()

        if col.isValid():
            color = 1./255*np.array(col.getRgb()[:3])
            self._rgbColorChanged.emit(*color)

    def setStackUnits(self,px,py,pz):
        for e,p in zip(self.stackEdits,[px,py,pz]):
            e.setText(str(p))

    def setBounds(self,x1,x2,y1,y2,z1,z2):
        for x,s in zip([x1,x2,y1,y2,z1,z2],self.sliderBounds):
            flag = s.blockSignals(True)
            s.setValue(x*100)
            s.blockSignals(flag)


    def boundsChanged(self):
        bounds = [s.value()/100. for s in self.sliderBounds]
        self._boundsChanged.emit(*bounds)


    def alphaPowChanged(self):
        alphaPow = 100.*(self.sliderAlphaPow.value()/100.)**3
        self._alphaPowChanged.emit(alphaPow)

    def stackUnitsChanged(self):
        try:
            stackUnits = [float(e.text()) for e in self.stackEdits]
            self._stackUnitsChanged.emit(*stackUnits)
        except Exception as e:
            print "couldnt parse text"
            print e
        
class MainWindow(QtGui.QMainWindow):

    def __init__(self, ):
        super(QtGui.QMainWindow,self).__init__()

        self.resize(500, 300)
        self.setWindowTitle('Test')

        self.settings = VolumeSettingsPanel()
        self.setCentralWidget(self.settings)
        self.setStyleSheet("background-color:black;")

    def close(self):
        QtGui.qApp.quit()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    win = MainWindow()
    win.show()
    win.raise_()

    sys.exit(app.exec_())