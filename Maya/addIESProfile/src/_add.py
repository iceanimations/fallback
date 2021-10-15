'''
Created on Apr 15, 2015

@author: qurban.ali
'''

import pymel.core as pc
import appUsageApp
from uiContainer import uic
import qtify_maya_window as qtfy
from PyQt4.QtGui import QMessageBox, QFileDialog
import msgBox
import os.path as osp
import qutil
#from loader.command.python import RedshiftAOVTools

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

__title__ = 'Add Profile'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Window(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.browseButton.clicked.connect(self.setPath)
        self.addButton.clicked.connect(self.addProfile)
        
        appUsageApp.updateDatabase('addIESProfile')
        
    def setPath(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File',
                                               '', '*.ies')
        if filename:
            self.pathBox.setText(filename)
    
    def getPath(self):
        path = self.pathBox.text()
        if not path or not osp.exists(path):
            self.showMessage(msg='The system could not find the path specified',
                             icon=QMessageBox.Information)
            path = ''
        return path
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=__title__, **kwargs)
        
    def setStatus(self, msg):
        self.statusBar().showMessage(msg, 2000)
        
    def getSelectedIESs(self):
        lights = pc.ls(sl=True, type=pc.nt.RedshiftIESLight, dag=True)
        if not lights:
            self.showMessage(msg='No IES Light found in the selection',
                             icon=QMessageBox.Information)
        return lights
        
    def addProfile(self):
        lights = self.getSelectedIESs()
        path = self.getPath()
        if lights and path:
            for light in lights:
                light.profile.set(path)
            self.setStatus('Profile added successfully')
    
    def closeEvent(self, event):
        self.deleteLater()