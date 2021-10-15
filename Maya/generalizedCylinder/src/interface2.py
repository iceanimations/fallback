import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt

site.addsitedir(r"R:\Pipe_Repo\Users\Hussain\packages")
import qtify_maya_window as qtfy

import os.path as osp
import sys

import polyRope as pr
reload(pr)

selfPath = sys.modules[__name__].__file__
rootPath = osp.dirname(osp.dirname(selfPath))
uiPath = osp.join(rootPath, 'ui')
uiFile = osp.join(uiPath, 'window2.ui')

Form, Base = uic.loadUiType(uiFile)
class Window(Form, Base):
    def __init__(self, parent = qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.stop = False
        self.progressBar.hide()
        self.stopButton.hide()
        self.setAttribute(Qt.WA_DeleteOnClose)

        #connections
        self.createButton.clicked.connect(self.create)
        self.resetButton.clicked.connect(self.reset)
        self.stopButton.clicked.connect(self.setStop)
        
        #method calls
        self.initUi()
        
    def initUi(self):
        values = pr.optionVars()
        if values == 0:
            return
        
        self.selectionButton.setChecked(bool(values[0]))
        self.samplesPerLengthBox.setValue(values[1])
        self.twistRateBox.setValue(values[2])
        self.brushWidthBox.setValue(values[3])
        self.adjustUVsButton.setChecked(bool(values[4]))
        self.closeEndsButton.setChecked(bool(values[5]))
        self.showButton.setChecked(bool(values[6]))
        self.numOfCylindersBox.setValue(int(values[7]))
        self.samplesPerLengthBox2.setValue(values[8])
        self.sectionsBox.setValue(int(values[9]))
        self.twistRateBox2.setValue(values[10])
        self.widthBox.setValue(values[11])
        self.adjustUVsButton2.setChecked(bool(values[12]))
        self.closeEndsButton2.setChecked(bool(values[13]))

    def setStop(self):
        self.stop = True

    def create(self):
        selection = self.selectionButton.isChecked()
        curves = pr.pc.ls(sl = selection, type = 'nurbsCurve', dag = True,
                geometry = True)
        for curve in curves:
            if type(curve) != pr.pc.nt.NurbsCurve:
                curves.remove(curve)
        if not curves:
            if selection:
                pr.pc.warning("No curve selected")
            else:
                pr.pc.warning("No curve found in the scene")
            return
        self.progressBar.setMaximum(len(curves))
        self.progressBar.show()
        self.stopButton.show()
        self.createButton.hide()
        qApp.processEvents()
        done = []
        for curve in curves:
            try:
                pr.pc.undoInfo(openChunk = True)
                pr.polyRope(curve, midSamplesPerLength=float(self.samplesPerLengthBox.value()),
                            midTwistRate=float(self.twistRateBox.value()),
                            midWidth=float(self.brushWidthBox.value()),
                            midRebuildSpansMult = 4,
                            midAdjustUVs=self.adjustUVsButton.isChecked(),
                            midCloseEnds=self.closeEndsButton.isChecked(),
                            numSideCyls=int(self.numOfCylindersBox.value()),
                            showMidCylinder=int(self.showButton.isChecked()),
                            sideSamplesPerLength=float(self.samplesPerLengthBox2.value()),
                            sideTwistRate=float(self.twistRateBox2.value()),
                            sideWidth=float(self.widthBox.value()),
                            sideRebuildSpansMult=4,
                            sideAdjustUVs=self.adjustUVsButton2.isChecked(),
                            sideCloseEnds=self.closeEndsButton2.isChecked(),
                            sideTubeSections=int(self.sectionsBox.value()))
                done.append(curve)
                self.progressBar.setValue(len(done))
                qApp.processEvents()
                if self.stop:
                    self.stop = False
                    break
            finally:
                pr.pc.undoInfo(closeChunk = True)
        
        self.stopButton.hide()
        self.createButton.show()
        self.progressBar.hide()
        qApp.processEvents()


    def reset(self):
        self.selectionButton.setChecked(True)
        self.samplesPerLengthBox.setValue(1)
        self.twistRateBox.setValue(3)
        self.brushWidthBox.setValue(1)
        self.adjustUVsButton.setChecked(True)
        self.closeEndsButton.setChecked(True)
        self.showButton.setChecked(False)

        self.numOfCylindersBox.setValue(4)
        self.samplesPerLengthBox2.setValue(1)
        self.sectionsBox.setValue(4)
        self.twistRateBox2.setValue(1.0)
        self.widthBox.setValue(1)
        self.adjustUVsButton2.setChecked(True)
        self.closeEndsButton2.setChecked(True)
        
    def closeEvent(self, event):
        self.saveState()
        
    def saveState(self):
        values = [float(self.selectionButton.isChecked()),
                  self.samplesPerLengthBox.value(),
                  self.twistRateBox.value(),
                  self.brushWidthBox.value(),
                  float(self.adjustUVsButton.isChecked()),
                  float(self.closeEndsButton.isChecked()),
                  float(self.showButton.isChecked()),
                  float(self.numOfCylindersBox.value()),
                  self.samplesPerLengthBox2.value(),
                  float(self.sectionsBox.value()),
                  self.twistRateBox2.value(),
                  self.widthBox.value(),
                  float(self.adjustUVsButton2.isChecked()),
                  float(self.closeEndsButton2.isChecked())]
        pr.addOptionVar(values)