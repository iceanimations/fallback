import pymel.core as pc
import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
import qtify_maya_window as mayaWin
import sys
import os.path as osp

Form, Base = uic.loadUiType('%s\window.ui'%osp.dirname(sys.modules
                                                       [__name__].__file__))
class Window(Form, Base):
    def __init__(self, parent = mayaWin.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.ignoreButton.clicked.connect(self.handleIgnoreButton)
        self.materialButton.clicked.connect(self.handleSingleMultiple)
        self.meshButton.clicked.connect(self.handleSingleMultiple)
        self.closeButton.clicked.connect(self.close)
        self.createButton.clicked.connect(self.createNodes)
        try:
            self.miMaterialsList = [pc.nt.Mia_material,
                                pc.nt.Mia_material_x,
                                pc.nt.Mia_material_x_passes]
        except: pc.warning("MentalRay material 'Mia_material_x_passes' not found")
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def handleSingleMultiple(self):
        if self.materialButton.isChecked():
            self.selectionLabel.setText("Select Mental Ray nodes from scene")
        else: self.selectionLabel.setText("Select mesh(es) from scene")
    
    def handleIgnoreButton(self):
        self.removeGammaButton.setChecked(self.ignoreButton.isChecked())
        self.removeGammaButton.setEnabled(self.ignoreButton.isChecked())
        
    def createNodes(self):
        ignoreGamma = self.ignoreButton.isChecked()
        removeGamma = self.removeGammaButton.isChecked()
        removeMiNodes = self.removeMiButton.isChecked()
        if self.materialButton.isChecked():
            mtls = pc.ls(sl = True)
            if not mtls:
                pc.warning('No selection found in the scene')
                return
            for mtl in mtls:
                if type(mtl) not in self.miMaterialsList:
                    pc.warning("Selection is not mi node " + str(mtl))
                    mtls.remove(mtl)
        else:
            mtls = self.miMaterials()
            if not mtls:
                return
        if mtls:
            self.miaToArnold(mtls,ignoreGamma,removeGamma,removeMiNodes)


    def miMaterials(self):
        '''
        returns the materials and shading engines
        @param:
            selection: if True, returns the materials and shading engines
            of selected meshes else all
        @return: dictionary {material: [shadingEngine1, shadingEngine2, ...]}
        '''
        materials = set()
        sg = set()
            #meshes = getMeshes(selection = selection)
        meshes = pc.ls(sl=True, dag=True, type='mesh')
        if not meshes:
            pc.warning("No selection or selection is not mesh")
            return
        for mesh in meshes:
            for s in pc.listConnections(mesh, type = 'shadingEngine'):
                sg.add(s)
        for x in sg:
            try:
                materials.add(x.miPhotonShader.inputs()[0])
                materials.add(x.miMaterialShader.inputs()[0])
                materials.add(x.miShadowShader.inputs()[0])
            except: pass
        if not materials:
            pc.warning("No mi material found on seleced mesh")
            return
        return list(materials)

    def miaToArnold(self, materials, ignoreGamma, rmGamma, rmMi):
        '''from mental ray to arnold'''
        for mentalRay in materials:
            aicmd = 'createRenderNodeCB -asShader "surfaceShader" aiStandard ""'
            arnold = pc.PyNode(pc.Mel.eval(aicmd))
            pc.rename(arnold, str(mentalRay))
            for conn in pc.listConnections(arnold):
                if type(conn) == pc.nt.ShadingEngine:
                    pc.delete(conn)
            for node in pc.listConnections(mentalRay):
                print node
                if type(node) == pc.nt.ShadingEngine:
                    pc.disconnectAttr(node.miPhotonShader)
                    pc.disconnectAttr(node.miMaterialShader)
                    pc.disconnectAttr(node.miShadowShader)
                    arnold.outColor >> node.surfaceShader
                if type(node) == pc.nt.File:
                    node.outColor >> arnold.KsColor
                if type(node) == pc.nt.Bump2d or type(node) == pc.nt.Bump3d:
                    node.outNormal >> arnold.normalCamera
                if type(node) == pc.nt.Mib_amb_occlusion:
                    arnold.color.set(node.bright.get())
                    print 'hello'
                if type(node) == pc.nt.GammaCorrect:
                    try:
                        if ignoreGamma:
                                for nod in pc.listConnections(node):
                                    if type(nod) == pc.nt.File:
                                        nod.outColor >> arnold.color
                                        break
                        else: node.outValue >> arnold.color
                        if rmGamma:
                            pc.delete(node)
                    except: pass
            if rmMi:
                pc.delete(mentalRay)
            else: 
                pc.disconnectAttr(mentalRay.reflectivity)
                pc.disconnectAttr(mentalRay.refl_color)
                pc.disconnectAttr(mentalRay.overall_bump)
                pc.disconnectAttr(mentalRay.diffuse)