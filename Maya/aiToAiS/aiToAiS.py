import pymel.core as pc
import site
site.addsitedir(r"R:/Python_Scripts")
site.addsitedir(r"R:\Pipe_Repo\Users\Hussain\packages")
from PyQt4.QtGui import *
from PyQt4 import uic
import qtify_maya_window as mayaWin
import sys
import os.path as osp

Form, Base = uic.loadUiType('%s\window.ui'%osp.dirname(sys.modules
                                                       [__name__].__file__))
class Window(Form, Base):
    def __init__(self, parent = mayaWin.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.materialButton.clicked.connect(self.handleSingleMultiple)
        self.meshButton.clicked.connect(self.handleSingleMultiple)
        self.closeButton.clicked.connect(self.close)
        self.createButton.clicked.connect(self.createNodes)
        
        # update the database, how many times this app is used
        site.addsitedir(r'r:/pipe_repo/users/qurban')
        import appUsageApp
        appUsageApp.updateDatabase('aiToAiS')
        
    def handleSingleMultiple(self):
        '''This function is responsible for the display of message what type
        of object to select from the scene'''
        if self.materialButton.isChecked():
            self.selectionLabel.setText("Select Mental Ray nodes from scene")
        else: self.selectionLabel.setText("Select mesh(es) from scene")
        
    def createNodes(self):
        '''This function call the aiToAiS function to replace the Ai nodes
        with AiS nodes'''
        removeAiNodes = self.removeAiButton.isChecked()
        if self.materialButton.isChecked():
            mtls = pc.ls(sl = True)
            if not mtls:
                pc.warning('No selection found in the scene')
                return
            for mtl in mtls:
                if type(mtl) != pc.nt.AiStandard:
                    pc.warning(str(mtl) +"Selection is not Ai node...")
                    print 'Removing '+ str(mtl) + ' from the selection list...'
                    mtls.remove(mtl)
        else:
            mtls = self.aiMaterials()
            if not mtls:
                return
        if mtls:
            self.aiToAiS(mtls, removeAiNodes)

    def aiMaterials(self):
        '''
        returns the Ai materials and their shading engines
        @return: list of materials
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
                materials.add(x.surfaceShader.inputs()[0])
            except: pass
        if not materials:
            pc.warning("No mi material found on seleced mesh")
            return
        return list(materials)

    def aiToAiS(self, materials, rmAi):
        '''from arnold to arnold standard'''
        for material in materials:
            aiscmd = 'createRenderNodeCB -asShader "surfaceShader" alSurface ""'
            aiSurface = pc.PyNode(pc.Mel.eval(aiscmd))
            pc.rename(aiSurface, 'aiSurface_'+ str(material).split(':')[-1].replace('aiStandard', ''))
            for conn in pc.listConnections(aiSurface):
                if type(conn) == pc.nt.ShadingEngine:
                    pc.delete(conn)
            # connect the shading engine
            for shEngine in pc.listConnections(material, type='shadingEngine'):
                shEngine.surfaceShader.disconnect()
                aiSurface.outColor.connect(shEngine.surfaceShader)
            try:
                outNormal = material.normalCamera.inputs(p=1)[0]
                #outNormal.disconnect()
                outNormal.connect(aiSurface.normalCamera)
            except: pass
            try:
                outColor1 = material.color.inputs(p=1)[0]
                #outColor1.disconnect()
                outColor1.connect(aiSurface.diffuseColor)
            except: pass
            try:
                outColor2 = material.KsColor.inputs(p=1)[0]
                #outColor2.disconnect()
                outColor2.connect(aiSurface.specular1Color)
            except: pass
            # set the attributes
            aiSurface.diffuseStrength.set(material.Kd.get())
            aiSurface.diffuseRoughness.set(material.diffuseRoughness.get())
            aiSurface.specular1Strength.set(material.Ks.get())
            aiSurface.specular1Roughness.set(material.specularRoughness.get())
            # remove the ai node
            if rmAi:
                pc.delete(material)