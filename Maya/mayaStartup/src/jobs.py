'''
Created on Jul 6, 2015

@author: qurban.ali
'''
import pymel.core as pc

from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog, qApp, QPushButton, QRadioButton, QDialog
import os
import re
import cui
reload(cui)
import os.path as osp
import qtify_maya_window as qtfy
import pymel.core as pc
import appUsageApp
import msgBox
import qutil
reload(qutil)
import re
import maya.cmds as cmds

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class FPSDialog(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(FPSDialog, self).__init__(parent)
        self.setupUi(self)
        
        for key in qutil.FPS_MAPPINGS:
            self.fpsBox.addItem(key)
            
        # set the current fps
        fps = self.getCurrentFPS()
        for i in range(self.fpsBox.count()):
            if fps in self.fpsBox.itemText(i):
                self.fpsBox.setCurrentIndex(i)
                break
        
        self.okButton.clicked.connect(self.ok)
        
    def getCurrentFPS(self):
        return pc.currentUnit(time=True, q=True)
    
    def getSelectedFPS(self):
        return self.fpsBox.currentText()
    
    def ok(self):
        fps = self.getSelectedFPS()
        for key in qutil.FPS_MAPPINGS:
            if fps in key:
                val = qutil.FPS_MAPPINGS[key]
                pc.currentUnit(time=val)
                pc.optionVar(sv=("workingUnitTime", val))
                pc.optionVar(sv=("workingUnitTimeDefault", val))
                break
        self.close()

def showFPSDialog():
    if cmds.file(q=True, location=True) == 'unknown':
        return
    FPSDialog().show()