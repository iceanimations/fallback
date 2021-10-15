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
site.addsitedir(r"R:/Pipe_Repo/Users/Qurban/utilities")
import qtify_maya_window as utl
try:
    from uiContainer import uic
except:
    from PyQt4 import uic
import PyQt4
from PyQt4 import QtGui, QtCore
import os.path as osp
import time
import appUsageApp
reload(appUsageApp)

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
        
        appUsageApp.updateDatabase('AOVEnable')

    def updateWindow(self):
        '''
        refreshes the list of passes in the GUI
        '''
        try:
            elements = pc.ls(type=pc.nt.AiAOV)
        except AttributeError:
            pc.warning("Arnold plugin not loaded")
            return
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
            # list existing pass(es) and their set(s)
            elements = pc.ls(type=pc.nt.AiAOV)
            if not elements:
                pc.warning('AOVs not found...')
                return
        except AttributeError:
            pc.warning('Arnold plugin not loaded...')
            return
        for element in elements:
            enabled = element.enabled.get()
            self.renderElements[element] = enabled
            name = element.attr('name').get()
            if name in [n.text() for n in self.elementButtons]:
                continue
            elementButton = QtGui.QCheckBox(name, self)
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
            if text == element.attr('name').get():
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
        element.enabled.set(val)
            
    def closeEvent(self, event):
        self.thread.terminate()
        self.deleteLater()
            
class Thread(QtCore.QThread):
    def __init__(self, parent = None):
        super(Thread, self).__init__(parent)
        self.parentWin = parent
        
    def run(self):
        while True:
            time.sleep(0.3)
            self.parentWin.refreshButton.released.emit()