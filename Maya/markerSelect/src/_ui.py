'''
Created on Jan 27, 2017

@author: qurban.ali
'''
from uiContainer import uic
import qtify_maya_window as qtfy
from PyQt4.QtGui import QMessageBox
import iutil
import os.path as osp
import appUsageApp
import pymel.core as pc
import cui

rootPath = iutil.dirname(__file__, 2)
uiPath = osp.join(rootPath, 'ui')
__title__ = 'Marker Select'

Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
class Window(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(__title__)
        
        self.setButton.clicked.connect(self.setMarkers)
        map(lambda btn: btn.clicked.connect(lambda: self.selectMarkers(btn.text())), [self.leftButton, self.rightButton, self.centerButton])
        
        self.left = []
        self.right = []
        self.center = []
        
        self.setButton.setFocus()
        
        appUsageApp.updateDatabase('MarkerSelect')
        
    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=__title__, **kwargs)
        
    def setMarkers(self):
        curves = pc.ls(sl=True, type='nurbsCurve', ni=True, dag=True)
        if not curves:
            self.showMessage(msg='No selected NurbsCurve found in the scene',
                             icon=QMessageBox.Information)
            return
        del self.center[:]
        del self.left[:]
        del self.right[:]
        for node in curves:
            name = node.firstParent()
            if name.endswith(self.centerMarkerBox.text()):
                self.center.append(name)
            if name.endswith(self.leftMarkerBox.text()):
                self.left.append(name)
            if name.endswith(self.rightMarkerBox.text()):
                self.right.append(name)
        self.selectMarkers([btn for btn in [self.centerButton, self.leftButton, self.rightButton] if btn.isChecked()][0].text())
    
    def selectMarkers(self, text):
        if text == 'Left':
            pc.select(self.left)
        if text == 'Right':
            pc.select(self.right)
        if text == 'Center':
            pc.select(self.center)