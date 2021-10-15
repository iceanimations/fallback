'''
Created on Oct 29, 2015

@author: qurban.ali
'''

from uiContainer import uic
import qtify_maya_window as qtfy
from PyQt4.QtGui import QMessageBox, QFileDialog
import pymel.core as pc
import os.path as osp
import iutil
import cui
import appUsageApp
import imaya
import subprocess

rootPath = iutil.dirname(__file__, 2)
uiPath = osp.join(rootPath, 'ui')

Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
class UI(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.title = 'Duplicate Per Frame'
        
        self.setWindowTitle(self.title)
        
        self.browseButton.clicked.connect(self.setPath)
        self.createButton.clicked.connect(self.create)
        
        appUsageApp.updateDatabase('DuplicatePerFrame')
        
    def create(self):
        path = self.getPath()
        if path:
            try:
                obj = pc.ls(sl=True, type='mesh', dag=True)[0].firstParent()
            except IndexError:
                self.showMessage(msg='No object selected in the scene')
                return
            duplicates = []
            for frame in range(*self.frameRange()):
                pc.currentTime(frame)
                pc.select(obj)
                duplicates.append(pc.duplicate(rr=1))
            if duplicates:
                pc.select(duplicates)
                pc.mel.doGroup(0, 1, 1)
                group = pc.ls(sl=True)
                pc.rename(group, imaya.getNiceName(obj) +'_duplicates_group')
                if self.includeButton.isChecked():
                    pc.select(obj, add=1)
                pc.exportSelected(osp.join(path, imaya.getNiceName(obj)).replace('\\', '/') +'_duplicates.ma',
                                  force=1, options="v=0;", typ="mayaAscii",
                                  pr=1)
                if self.removeButton.isChecked():
                    pc.delete(group)
                if self.openButton.isChecked():
                    subprocess.Popen('explorer %s'%osp.normpath(path))
        
    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=self.title, **kwargs)
    
    def setPath(self):
        filename = QFileDialog.getExistingDirectory(self, self.title, '', QFileDialog.DontUseNativeDialog|QFileDialog.ShowDirsOnly)
        if filename:
            self.pathBox.setText(filename)
    
    def getPath(self):
        path = self.pathBox.text()
        if not osp.exists(path):
            self.showMessage(msg='The system could not find the path specified',
                             icon=QMessageBox.Information)
            path = ''
        return path
    
    def frameRange(self):
        return self.startRangeBox.value(), self.endRangeBox.value() + 1
        