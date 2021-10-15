from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
import qtify_maya_window as qtfy

import os.path as osp
import sys

import pymel.core as pc

selfPath = sys.modules[__name__].__file__
rootPath = osp.dirname(osp.dirname(selfPath))
uiPath = osp.join(rootPath, 'ui')
uiFile = osp.join(uiPath, 'window.ui')

Form, Base = uic.loadUiType(uiFile)
class Window(Form, Base):
    def __init__(self, parent = qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.closeButton.clicked.connect(self.close)
        self.createButton.clicked.connect(self.create)
        
    def materials(self):
        materials = []
        if self.materialButton.isChecked():
            materials[:] = pc.ls(sl = True, type = 'aiStandard')
        else:
            meshes = pc.ls(sl = True, type = 'mesh', dag = True)
            for mesh in meshes:
                for sg in pc.listConnections(mesh, type = 'shadingEngine'):
                    for mtrl in pc.listConnections(sg, type = 'aiStandard'):
                        materials.append(mtrl)
        if not materials:
            pc.warning('No selection or no "aiStandard" found in the selection')
        return list(set(materials))
        
    def create(self):
        removeAi = self.removeAiButton.isChecked()
        for node in self.materials():
            
            name = str(node)
            newName = name.replace('aiStandard', 'VRayMtl')
            vraycmd = 'createRenderNodeCB -asShader "surfaceShader" VRayMtl ""'
            vrayMtl = pc.PyNode(pc.Mel.eval(vraycmd))
            
            try:
                node.color.inputs(plugs = True)[0].connect(vrayMtl.color, f=True)
            except IndexError:
                vrayMtl.color.set(node.color.get())
            try:
                node.normalCamera.inputs(plugs=True)[0].connect(vrayMtl.bumpMap, f=True)
            except IndexError:
                pass
            
            for shEng in pc.listConnections(node, type = 'shadingEngine'):
                vrayMtl.outColor.connect(shEng.surfaceShader, f=True)
            if removeAi:
                pc.delete(node)
            else:
                pc.rename(node, str(node)+'tempNode')
            pc.rename(vrayMtl, newName)