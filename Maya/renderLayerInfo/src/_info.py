'''
Created on Feb 23, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
import os.path as osp
import qtify_maya_window as qtfy
import pymel.core as pc
from collections import OrderedDict
import imaya
import appUsageApp

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')

Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
class Info(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Info, self).__init__(parent)
        self.setupUi(self)
        
        self.displayInfo()
        
        appUsageApp.updateDatabase('RenderLayerInfo')
        
    def getRenderLayerInfo(self, renderLayer):

        currentLayer = pc.editRenderLayerGlobals(q=1, crl=1)
        if currentLayer != renderLayer:
            pc.editRenderLayerGlobals(crl=renderLayer)
    
        info = OrderedDict()
        info['cameras'] = [str(cam.firstParent()) for cam in imaya.getCameras(True, False)]
        val = 'Enabled' if pc.getAttr('defaultRenderGlobals.animation') else 'Disabled'
        info['range']   = str(imaya.getFrameRange()) + ' - Animation: %s'%val
        info['passes']  = [str(aov)
                for aov in pc.ls(type='RedshiftAOV')
                if aov.enabled.get()]
        info['resolution'] = str(imaya.getResolution())
    
        return info

    def gatherRenderLayersInfo(self):
        currentLayer = pc.editRenderLayerGlobals(q=1, crl=1)
        layerInfo = OrderedDict()
        for crl in imaya.getRenderLayers():
            layerInfo[str(crl)]=self.getRenderLayerInfo(crl)
        pc.editRenderLayerGlobals(crl=currentLayer)
        return layerInfo
    
    def displayInfo(self):
        info = self.gatherRenderLayersInfo()
        for key, value in info.items():
            item = Item(self)
            item.setTitle(key)
            item.setCamera(', '.join(value['cameras']))
            item.setFrame(value['range'])
            item.setPasses(value['passes'])
            item.setResolution(value['resolution'])
            self.itemLayout.addWidget(item)
        
Form1, Base1 = uic.loadUiType(osp.join(uiPath, 'item.ui'))
class Item(Form1, Base1):
    def __init__(self, parent=None):
        super(Item, self).__init__(parent)
        self.setupUi(self)
        self.parentWin = parent
        self.collapsed = False
        self.style = ('background-image: url(%s);\n'+
                      'background-repeat: no-repeat;\n'+
                      'background-position: center right')
        self.collapse()
        self.iconLabel.setStyleSheet(self.style%osp.join(iconPath, 'ic_expand.png').replace('\\', '/'))
        self.titleFrame.mouseReleaseEvent = self.collapse
        self.titleFrame.setCursor(QCursor(Qt.PointingHandCursor))

    def collapse(self, event=None):
        if self.collapsed:
            self.frame.show()
            self.collapsed = False
            path = osp.join(iconPath, 'ic_collapse.png')
        else:
            self.frame.hide()
            self.collapsed = True
            path = osp.join(iconPath, 'ic_expand.png')
        path = path.replace('\\', '/')
        self.iconLabel.setStyleSheet(self.style%path)

    def toggleCollapse(self, state):
        self.collapsed = not state
        self.collapse()

    def setTitle(self, title):
        self.nameLabel.setText(title)

    def setCamera(self, camera):
        self.cameraLabel.setText(camera)

    def setFrame(self, frame):
        self.frameLabel.setText(frame)
    
    def setPasses(self, passes):
        self.passesBox.view().setAttribute(Qt.WA_Disabled, True)
        self.passesBox.view().setAttribute(Qt.WA_MouseTracking, False)
        self.passesBox.addItems(passes)
    
    def setResolution(self, res):
        self.resolutionLabel.setText(res)