import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
import qtify_maya_window as qtfy

import os.path as osp
import sys
import time
import pymel.core as pc

import appUsageApp
reload(appUsageApp)


Form, Base = uic.loadUiType(r'%s\ui\window.ui'%osp.dirname(osp.dirname(__file__)))

class Window(Form, Base):
    def __init__(self, parent = qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        self.closeButton.clicked.connect(self.close)
        self.convertButton.clicked.connect(self.convert)
        self.selectButton.clicked.connect(self.selectVRay)
        self.progressBar.hide()
        
        # update the database, how many times this app is used
        appUsageApp.updateDatabase('VRayToArnold') 
        
    
    def closeEvent(self, event):
        self.deleteLater()
        
    def selectVRay(self):
        mtls = pc.ls(type=pc.nt.VRayMtl)
        num = len(mtls)
        msg = ' materials selected'
        if num == 1: msg = ' material selected'
        if num == 0: msg = 'No material found'; num=''
        pc.select(mtls)
        self.materialLabel.setText(str(num) + msg)
        qApp.processEvents()
        time.sleep(1)
        self.materialLabel.setText('')
        
    def materials(self):
        materials = []
        if self.materialButton.isChecked():
            materials[:] = pc.ls(sl = True, type = pc.nt.VRayMtl)
            temp = set()
            temp2 = []
            for mtl in materials:
                outputs = mtl.outColor.connections(d=True, type=pc.nt.VRayBlendMtl)
                if outputs:
                    temp2.append(mtl)
                    for output in outputs:
                        temp.add(output)
            for t1 in temp2:
                materials.remove(t1)
                
            for t2 in temp:
                materials.append(t2)
            
        elif self.meshButton.isChecked():
            meshes = pc.ls(sl = True, type = 'mesh', dag = True)
            for mesh in meshes:
                for sg in pc.listConnections(mesh, type = 'shadingEngine'):
                    try:
                        mtrl = sg.surfaceShader.inputs()[0]
                    except:
                        continue
                    if type(mtrl) == pc.nt.VRayMtl or type(mtrl) == pc.nt.VRayBlendMtl:
                        materials.append(mtrl)
        if not materials:
            pc.warning('No selection or no Material found in the selection')
        return list(set(materials))
    
    def convert(self):
        self.progressBar.show()
        mtls = self.materials()
        num = len(mtls)
        self.progressBar.setMaximum(num)
        done = []
        for node in mtls:
            self.progressBar.setValue(len(done))
            if type(node) == pc.nt.VRayBlendMtl:
                self.handleBlendMtl(node)
                continue
            arnold = self.createArnold(node)
            if arnold == None:
                return
            for shEng in pc.listConnections(node, type = 'shadingEngine'):
                shEng.surfaceShader.disconnect()
                arnold.outColor.connect(shEng.surfaceShader)
            if self.removeButton.isChecked():
                pc.delete(node)
            done.append(node)
        self.progressBar.hide()
        
    def createArnold(self, node):
        aicmd = 'createRenderNodeCB -asShader "surfaceShader" aiStandard ""'
        try:
            arnold = pc.PyNode(pc.Mel.eval(aicmd))
        except:
            pc.warning("Seems like Arnod is either not installed or not loaded")
            return None
        for sg in pc.listConnections(arnold, type=pc.nt.ShadingEngine):
            pc.delete(sg)
        name = str(node)
        try:
            pc.rename(node, name +"_temp_node")
        except RuntimeError as re:
            pc.warning('Can not rename \"'+node+'\"')
        newName = name.replace('VRayMtl', "aiStandard")
        pc.rename(arnold, newName)
        
        mapping = {'color':'color', 'reflectionColor': 'KsColor', 'refractionColor': 'KtColor',
                   'illumColor':'emissionColor', 'diffuseColorAmount': 'Kd',
                   'roughnessAmount': 'diffuseRoughness', 'reflectionColorAmount': 'Ks',
                   #'transparency': 'opacity',
                   'refractionColorAmount': 'Kt', 'refractionIOR': 'IOR',
                   'hilightGlossiness': 'specularRoughness', 'refractionGlossiness': 'refractionRoughness'}
#                   'anisotropy': 'specularAnisotropy', 'anisotropyRotation': 'specularRotation'}
        
#         if node.anisotropy.get() or node.anisotropyRotation.get():
#             arnold.specularBrdf.set(1)
        arnold.specularFresnel.set(node.useFresnel.get())
        for src in mapping:
            tgt = mapping[src]
            source = pc.PyNode(str(node)+'.'+src)
            target = pc.PyNode(str(arnold)+'.'+tgt)
            attr = None
            try:
                fileNode = source.inputs()[0]
                if type(fileNode) == pc.nt.GammaCorrect:
                    source = fileNode.value
                attr = source.inputs(plugs=True)[0]
                source.disconnect()
                if type(fileNode) == pc.nt.GammaCorrect:
                    pc.delete(fileNode)
            except:
                value = source.get()
                if src == 'hilightGlossiness' or src == 'refractionGlossiness':
                    value = 1 - source.get()
                target.set(value)
            if attr:
                attr.connect(target, f=True)       
        
        try:
            fileNode = node.bumpMap.inputs()[0]
            bump2d = pc.createNode('bump2d')
            fileNode.outAlpha.connect(bump2d.bumpValue, f=True)
            bump2d.outNormal.connect(arnold.normalCamera, f=True)
            bump2d.bumpDepth.set(node.bumpMult.get())
        except:
            pass
        return arnold
                
    def uncheckOpaque(self, node, newName):
        shEngines = node.connections(type = pc.nt.ShadingEngine)
        for sg in shEngines:
            meshes = sg.dagSetMembers.inputs()
            meshes = pc.ls(meshes, type='mesh', dag=True)
            for mesh in meshes:
                if node.opacity.get() != (1,1,1):
                    mesh.aiOpaque.set(0)
                    
    def handleBlendMtl(self, blendMtl):
        blendMtlName = str(blendMtl)
        baseMtl = None
        try:
            baseMtl = blendMtl.base_material.inputs()[0]
        except:
            pass
        print baseMtl
        coatMtls = []
        for i in range(9):
            try:
                coatMtl = pc.PyNode(str(blendMtl)+'.coat_material_'+str(i)).inputs()[0]
                coatMtls.append(coatMtl)
            except:
                pass
        print coatMtls
        baseArnold = None
        if baseMtl:
            baseArnold = self.createArnold(baseMtl)
        coatArnolds = []
        for coatMtl in coatMtls:
            coatArnolds.append(self.createArnold(coatMtl))
        layeredTexture = pc.shadingNode('layeredTexture', asTexture=True)
        count = 0
        additive_mode = blendMtl.additive_mode.get()
        for coatMtl in coatArnolds:
            coatMtl.outColor.connect(layeredTexture.attr("inputs")[count].color)
            self.setAttr(pc.PyNode(str(blendMtl)+'.blend_amount_'+str(count)),
                         layeredTexture.attr("inputs")[count].alpha)
            if additive_mode:
                layeredTexture.attr("inputs")[count].blendMode.set(4)
            count += 1
        
        if baseArnold:
            baseArnold.outColor.connect(layeredTexture.attr("inputs")[count].color)
        newArnold = pc.shadingNode('aiStandard', asShader=True)
        pc.rename(blendMtl, blendMtlName + 'temp_blen_mtl')
        blendMtlName = blendMtlName.replace('VRayBlendMtl', 'aiStandard')
        pc.rename(layeredTexture, str(blendMtlName) +'_layeredTexture')
        pc.rename(newArnold, blendMtlName)
        for sg in pc.listConnections(newArnold, type=pc.nt.ShadingEngine):
            pc.delete(sg)
        layeredTexture.outColor.connect(newArnold.emissionColor)
        newArnold.color.set(0, 0, 0)
        newArnold.KsColor.set(0, 0, 0)
        newArnold.emission.set(1)
        for sg in pc.listConnections(blendMtl, type=pc.nt.ShadingEngine):
            newArnold.outColor.connect(sg.surfaceShader, f=True)
        if self.removeButton.isChecked():
            pc.delete([blendMtl, baseMtl] + coatMtls)
            
    def setAttr(self, source, target):
        attr = None
        try:
            node = source.inputs()[0]
            if type(node) == pc.nt.GammaCorrect:
                newNode = node.value.inputs()[0]
                pc.delete(node)
                attr = newNode.outAlpha
            else:
                attr = node.outAlpha
        except:
            values = source.get()
            target.set((values[0] + values[1] + values[2])/3)
        if attr:
            attr.connect(target, f=True)
