#-------------------------------------------------------------------------------
# Name:        enable_VRay_passes
# Purpose:     To enable or disable the VRay passes (VRayRenderElement)
#
# Author:      Qurban Ali (qurban.ali@iceanimations.com)
#
# Created:     29/12/2012
# Copyright:   (c) ice-animations (Pvt.) Ltd. 2012
# Licence:     <ice-animations>
#-------------------------------------------------------------------------------

import pymel.core as pc
import site
site.addsitedir(r"R:/Pipi_Repo/Users/Qurban/Utilities")
import qtify_maya_window as utl
try:
    from uiContainer import uic
except:
    from PyQt4 import uic
import PyQt4
from PyQt4 import QtGui, QtCore
import os.path as osp
import time

Form, Base = uic.loadUiType(r"%s\ui\ui.ui"%osp.dirname(__file__))
class UI(Form, Base):
    def __init__(self, parent = utl.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.elementButtons = [] # list of passes as checkBox
        self.renderElements = {}
        self.f = QtGui.QFont("Arial", 9)
        self.listPasses()
        self.refreshButton.released.connect(self.updateWindow)
        self.refreshButton.hide()
        self.thread = Thread(self)
        self.thread.start()
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('enable_VRay_passes')

    def updateWindow(self):
        '''
        refreshes the list of passes in the GUI
        '''
        elements = pc.ls(type = ['VRayRenderElement', 'VRayRenderElementSet'])
        newElements = {}
        for element in elements:
            newElements[element] = element.enabled.get()
        if self.renderElements != newElements:
            self.renderElements.clear()
            for btn in self.elementButtons:
                btn.hide()
                btn.deleteLater()
            self.elementButtons[:] = []
            self.listPasses()

    def listPasses(self):
        '''
        lists all the passes as checkBox within scrollArea on the GUI
        '''
        try:
            # list existing passe(s) (VRayRenderElements) and their set(s)
            elements = pc.ls(type = ['VRayRenderElement', 'VRayRenderElementSet'])
            if not elements:
                pc.warning('VRay elements not found...')
                return
        except RuntimeError:
            pc.warning('VRay plugin is not loaded...')
            return
        for element in elements:
            enabled = element.enabled.get()
            self.renderElements[element] = enabled
            elementButton = QtGui.QCheckBox(str(element), self)
            style = "border-bottom: 1px solid black; padding-bottom: 4px"
            elementButton.setStyleSheet(style)
            elementButton.setFont(self.f)
            self.elementButtons.append(elementButton)
            if enabled:
                elementButton.setChecked(True)
            self.elementsLayout.addWidget(elementButton)
        map(lambda btn: btn.clicked.connect(lambda: self.switchElement(btn)), self.elementButtons)

    def switchElement(self, btn):
        '''
        sets the enable property of the pass according to the checkBox on GUI
        '''
        text = str(btn.text())
        for element in self.renderElements:
            if text == str(element):
                try:
                    # override the the enable property of pass
                    pc.editRenderLayerAdjustment(element.enabled)
                except RuntimeError:
                    pass
                break
        if btn.isChecked():
            self.setEnDis(element, 1)
        else:
            self.setEnDis(element, 0)
            
    def setEnDis(self, element, val):
        try:
            element.enabled.set(val)
        except general.MayaNodeError:
            pc.warning('VRay element does not exists...')
            
    def closeEvent(self, event):
        self.thread.terminate()
        self.deleteLater()
        
    def hideEvent(self, event):
        self.close()
            
class Thread(QtCore.QThread):
    def __init__(self, parent = None):
        super(Thread, self).__init__(parent)
        self.parentWin = parent
        
    def run(self):
        while True:
            time.sleep(0.3)
            self.parentWin.refreshButton.released.emit()
        
        

def main():
    global ui
    ui = UI()
    ui.show()
