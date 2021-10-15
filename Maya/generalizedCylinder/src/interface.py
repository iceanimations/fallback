import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *

site.addsitedir(r"R:\Pipe_Repo\Users\Hussain\packages")
import qtify_maya_window as qtfy

import os.path as osp
import sys

import generalizedCylinder as gc

selfPath = sys.modules[__name__].__file__
rootPath = osp.dirname(osp.dirname(selfPath))
uiPath = osp.join(rootPath, 'ui')
uiFile = osp.join(uiPath, 'window.ui')

Form, Base = uic.loadUiType(uiFile)
class Window(Form, Base):
    def __init__(self, parent = qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.twistRateBox.setValue(0.5)
        self.curves = []
        self.stop = False
        self.progressBar.hide()
        self.stopButton.hide()
        
        #connections
        self.createButton.clicked.connect(self.create)
        self.resetButton.clicked.connect(self.reset)
        self.stopButton.clicked.connect(self.setStop)
        
    def setStop(self):
        self.stop = True
        
    def create(self):
        selection = self.selectionButton.isChecked()
        self.curves[:] = gc.pc.ls(sl = selection, type = 'nurbsCurve',
                          dag = True, geometry = True)
        for curve in self.curves:
            if type(curve) != gc.pc.nt.NurbsCurve:
                self.curves.remove(curve)
        if not self.curves:
            if selection:
                gc.pc.warning("No curve selected")
            else:
                gc.pc.warning("No curve found in the scene")
            return
        samples = float(self.samplesPerLengthBox.value())
        sections = int(self.tubeSectionsBox.value())
        tRate = float(self.twistRateBox.value())
        bWidth = float(self.brushWidthBox.value())
        self.progressBar.setMaximum(len(self.curves))
        self.progressBar.show()
        self.stopButton.show()
        self.createButton.hide()
        qApp.processEvents()
        done = []
        for curve in self.curves:
            gc.generalizedCylinder(curve, samplesPerLength=samples,
                                   tubeSections=sections,
                                   twistRate=tRate,
                                   brushWidth=bWidth)
            done.append(curve)
            self.progressBar.setValue(len(done))
            qApp.processEvents()
            if self.stop:
                self.stop = False
                break
        self.stopButton.hide()
        self.createButton.show()
        self.progressBar.hide()
        qApp.processEvents()
            
    
    def reset(self):
        self.selectionButton.setChecked(True)
        self.samplesPerLengthBox.setValue(2)
        self.tubeSectionsBox.setValue(4)
        self.twistRateBox.setValue(0.5)
        self.brushWidthBox.setValue(0.5)