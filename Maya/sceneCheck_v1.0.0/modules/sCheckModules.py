# Embedded file name: c:\sceneCheck_v1.0.0/modules\sCheckModules.py
"""
        assetPublisher Tool Barajoun Entertainment copyright(c)
        Pipeline TD: Domingos Silva
        
        MAYA MODULES
"""
import os
import sys
import re
import glob
import maya.OpenMaya as api
import maya.cmds as cmds
import maya.mel as mel
import shutil
import subprocess
from pprint import pprint

class mayaCmds(object):

    def __init__(self, parent = None):
        pass

    def checkNodeType(self, node):
        return cmds.nodeType(node)

    def selectNode(self, node):
        cmds.select(node, r=True)

    def getArnoldShaders(self):
        aiShaders = cmds.listNodeTypes('rendernode/arnold', ex='texture:light:shader/utility:shader/volume')
        if aiShaders is None:
            return []
        else:
            return aiShaders
            return

    def getAiConnectedShaders(self, shape):
        aiCShaders = []
        othCShaders = []
        multiSG = []
        aiShaders = self.getArnoldShaders()
        sgShaders = cmds.listConnections(shape, type='shadingEngine')
        if len(sgShaders) > 1:
            multiSG.append(shape)
        for sgShader in sgShaders:
            nodes = cmds.listConnections('%s.surfaceShader' % sgShader, source=True)
            if nodes:
                for node in nodes:
                    if cmds.nodeType(node) in aiShaders:
                        aiCShaders.append(node)
                    else:
                        othCShaders.append(node)

        return (multiSG, othCShaders, aiCShaders)

    def getFileNodesTexturesAssigend(self, shape):
        fileNodes = []
        texFiles = []
        udimTex = []
        ofileNodes = []
        oudimTex = []
        otexFiles = []
        otherNodes = []
        skipTex = []
        aiShaders = self.getArnoldShaders()
        sgShaders = cmds.listConnections(shape, type='shadingEngine')
        if sgShaders:
            for sgShader in sgShaders:
                nodes = cmds.listConnections('%s.surfaceShader' % sgShader, source=True)
                if nodes:
                    for node in nodes:
                        if cmds.nodeType(node) in aiShaders:
                            try:
                                cmds.setAttr('%s.shd' % shape, l=False)
                                cmds.setAttr('%s.shd' % shape, '%s' % sgShader, type='string')
                                cmds.setAttr('%s.shd' % shape, l=True)
                            except:
                                pass

                        fileTexNodes = cmds.listConnections(node, type='file')
                        bumpNodes = cmds.listConnections(node, type='bump2d')
                        dispNodes = cmds.listConnections(node, type='displacementShader')
                        if bumpNodes:
                            otherNodes += bumpNodes
                        if dispNodes:
                            otherNodes += dispNodes
                        if fileTexNodes:
                            for fnode in fileTexNodes:
                                texture = cmds.getAttr('%s.fileTextureName' % fnode)
                                texture.replace('\\', '/')
                                texture = cmds.workspace(expandName=texture)
                                udimTokens = re.split('.<udim>', texture)
                                if len(udimTokens) > 1:
                                    alltex = glob.glob('%s*%s' % (udimTokens[0], udimTokens[1]))
                                    for tex in alltex:
                                        tokens = self.getTonkenizedPath(tex)
                                        udimTex.append(tex)

                                tokens = self.getTonkenizedPath(texture)
                                texFiles.append(texture)
                                fileNodes.append(fnode)

                        if otherNodes:
                            for onode in otherNodes:
                                ofileTexNodes = cmds.listConnections(onode, type='file')
                                if ofileTexNodes:
                                    for ofnode in ofileTexNodes:
                                        texture = cmds.getAttr('%s.fileTextureName' % ofnode)
                                        texture.replace('\\', '/')
                                        texture = cmds.workspace(expandName=texture)
                                        udimTokens = re.split('.<udim>', texture)
                                        if len(udimTokens) > 1:
                                            alltex = glob.glob('%s*%s' % (udimTokens[0], udimTokens[1]))
                                            oudimTex.extend(alltex)
                                        otexFiles.append(texture)
                                        ofileNodes.append(ofnode)

        return {'nodes': fileNodes,
         'textures': texFiles,
         'udim': udimTex,
         'onodes': ofileNodes,
         'otextures': otexFiles,
         'oudim': oudimTex}

    def getShapesTextureFiles(self, prefix = ''):
        cmds.select(cl=True)
        try:
            cmds.select('%s_*' % prefix)
        except:
            cmds.select(all=True)

        shapes = cmds.ls(type='surfaceShape', sl=True, dag=True)
        if shapes is None:
            shapes = cmds.ls(type='surfaceShape')
        texDict = {}
        for shape in shapes:
            texDict[shape] = self.getFileNodesTexturesAssigend(shape)

        return texDict

    def checkTextureFiles(self):
        missingTex = {}
        files = cmds.ls(tex=True)
        for nodefile in files:
            try:
                texture = cmds.getAttr('%s.fileTextureName' % nodefile)
                texture = cmds.workspace(expandName=texture)
                texture.replace('\\', '/')
                udimTokens = re.split('.<udim>', texture)
                if len(udimTokens) > 1:
                    alltex = glob.glob('%s*%s' % (udimTokens[0], udimTokens[1]))
                    if len(alltex) == 0:
                        missingTex[nodefile] = texture
                elif os.path.exists(texture) and os.path.isfile(texture):
                    pass
                else:
                    missingTex[nodefile] = texture
            except:
                pass

        return missingTex

    def delExtraCamLight(self):
        delList = []
        defCams = ('frontShape', 'perspShape', 'sideShape', 'topShape')
        camLigths = cmds.ls(type=['camera', 'light'])
        for cl in camLigths:
            if cmds.nodeType(cl) == 'camera' and cl not in defCams:
                cmds.delete(cl)
                delList.append(cl)
            elif cl not in defCams:
                cmds.delete(cl)
                delList.append(cl)

        return delList

    def checkUVs(self, shape):
        nodeDagPath = api.MDagPath()
        component = api.MObject()
        selList = api.MSelectionList()
        selList.add(shape)
        selList.getDagPath(0, nodeDagPath, component)
        mfnMesh = api.MFnMesh(nodeDagPath)
        itPoly = api.MItMeshPolygon(nodeDagPath, component)
        uvprob = False
        uvnegative = False
        noUVs = []
        negUVs = []
        itPoly.reset(nodeDagPath, component)
        while not itPoly.isDone():
            index = itPoly.index()
            uArray = api.MFloatArray()
            vArray = api.MFloatArray()
            if not itPoly.hasUVs():
                noUVs.append(index)
                uvprob = True
            else:
                itPoly.getUVs(uArray, vArray)
                for i in range(uArray.length()):
                    if uArray[i] < -0.001 or vArray[i] < -0.001:
                        negUVs.append(index)
                        uvnegative = True
                        break

            itPoly.next()

        return (noUVs, negUVs)

    def checkRemoveRefs(self):
        curScene = cmds.file(q=True, sceneName=True)
        refs = cmds.file(curScene, q=True, reference=True)
        for ref in refs:
            cmds.file(ref, removeReference=True)

        return refs

    def deleteLayers(self):
        layers = cmds.ls(type=['displayLayer', 'renderLayer'])
        for layer in layers:
            if layer not in ('defaultRenderLayer', 'defaultLayer'):
                cmds.delete(layer)

    def deleteNonStaticChannel(self, node):
        attrs = cmds.listAttr(node, k=True)
        if attrs:
            for attr in attrs:
                try:
                    cmds.deleteAttr(node, attribute=attr)
                except:
                    pass

    def optimizeDefValues(self):
        optionVars = ('nurbsSrfOption', 'nurbsCrvOption', 'unusedNurbsSrfOption', 'locatorOption', 'clipOption', 'poseOption', 'ptConOption', 'pbOption', 'deformerOption', 'unusedSkinInfsOption', 'expressionOption', 'groupIDnOption', 'animationCurveOption', 'snapshotOption', 'unitConversionOption', 'shaderOption', 'cachedOption', 'transformOption', 'displayLayerOption', 'renderLayerOption', 'setsOption', 'partitionOption', 'referencedOption', 'brushOption', 'unknownNodesOption', 'shadingNetworksOption')
        cmds.optionVar(iv=('nurbsSrfOption', 1))
        cmds.optionVar(iv=('nurbsCrvOption', 0))
        cmds.optionVar(iv=('unusedNurbsSrfOption', 0))
        cmds.optionVar(iv=('locatorOption', 0))
        cmds.optionVar(iv=('clipOption', 0))
        cmds.optionVar(iv=('poseOption', 0))
        cmds.optionVar(iv=('ptConOption', 0))
        cmds.optionVar(iv=('pbOption', 1))
        cmds.optionVar(iv=('deformerOption', 0))
        cmds.optionVar(iv=('unusedSkinInfsOption', 1))
        cmds.optionVar(iv=('expressionOption', 0))
        cmds.optionVar(iv=('groupIDnOption', 1))
        cmds.optionVar(iv=('animationCurveOption', 1))
        cmds.optionVar(iv=('snapshotOption', 1))
        cmds.optionVar(iv=('unitConversionOption', 1))
        cmds.optionVar(iv=('shaderOption', 1))
        cmds.optionVar(iv=('cachedOption', 0))
        cmds.optionVar(iv=('transformOption', 1))
        cmds.optionVar(iv=('displayLayerOption', 1))
        cmds.optionVar(iv=('renderLayerOption', 1))
        cmds.optionVar(iv=('setsOption', 1))
        cmds.optionVar(iv=('partitionOption', 0))
        cmds.optionVar(iv=('referencedOption', 1))
        cmds.optionVar(iv=('brushOption', 1))
        cmds.optionVar(iv=('unknownNodesOption', 1))
        cmds.optionVar(iv=('shadingNetworksOption', 0))

    def setOptVariables(self, variables = []):
        for var in variables:
            cmds.optionVar(iv=(var['name'], var['value']))

    def sceneCheck(self, ref = False, cam = False, history = False, freezeTransf = False, nonStChannel = False, normal = False, UVs = False, aiShader = False, texture = False, polyCleanUp = False, shell = False, cleanUp = False):
        if os.name == 'nt':
            cmds.unloadPlugin('vrayformaya.mll', force=True)
            cmds.unloadPlugin('3delight_for_mayaX.mll', force=True)
            cmds.unloadPlugin('RenderMan_for_Maya.mll', force=True)
        else:
            cmds.unloadPlugin('vrayformaya.so', force=True)
            cmds.unloadPlugin('3delight_for_mayaX.so', force=True)
            cmds.unloadPlugin('RenderMan_for_Maya.so', force=True)
        objectsDict = {}
        missTex = []
        if ref:
            remRefs = self.checkRemoveRefs()
        if cam:
            delCamLights = self.delExtraCamLight()
        if texture:
            missTex = self.checkTextureFiles()
        cmds.select(cl=True)
        cmds.select(all=True)
        objs = cmds.ls(selection=True)
        for obj in objs:
            parent = cmds.listRelatives(obj, parent=True, type='transform')
            if freezeTransf:
                cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0)
            if nonStChannel:
                self.deleteNonStaticChannel(obj)
            namesp = cmds.namespaceInfo(currentNamespace=True)
            if namesp != ':':
                cmds.namespace(namesp, rm=True)
            transforms = cmds.listRelatives(obj, allDescendents=True, type=['transform', 'surfaceShape'])
            if transforms is not None:
                for transf in transforms:
                    multiSG = []
                    cOthers = []
                    cAiShaders = []
                    noUVs = []
                    negUVs = []
                    numShells = []
                    try:
                        if history:
                            cmds.delete(transf, ch=True)
                        nodeDagPath = api.MDagPath()
                        component = api.MObject()
                        selList = api.MSelectionList()
                        selList.add(transf)
                        selList.getDagPath(0, nodeDagPath, component)
                        nodeDagPath.extendToShape()
                        shapeName = nodeDagPath.partialPathName()
                        if aiShader:
                            multiSG, cOthers, cAiShaders = self.getAiConnectedShaders(shapeName)
                        if normal:
                            cmds.polyNormal(shapeName, nm=2)
                            cmds.delete(shapeName, ch=True)
                        cmds.select(shapeName, r=True)
                        if polyCleanUp:
                            mel.eval('polyCleanupArgList 3 {"0","1","0","0","0","0","0","0","1","1e-005","1","1e-005","0","1e-005","0","1","1"};')
                        if UVs:
                            noUVs, negUVs = self.checkUVs(shapeName)
                        if shell:
                            nshell = cmds.polyEvaluate(shapeName, shell=True)
                            if nshell > 1:
                                numShells.append(nshell)
                        if nonStChannel:
                            self.deleteNonStaticChannel(transf)
                        objectsDict[shapeName] = {'name': shapeName,
                         'aiShaderAssigned': cAiShaders,
                         'shaderAssigned': cOthers,
                         'perFaceAssigned': multiSG,
                         'faceNoUvs': noUVs,
                         'faceNegUvs': negUVs,
                         'nShells': numShells}
                    except Exception as msg:
                        pass

        if cleanUp:
            self.optimizeDefValues()
            mel.eval('source "cleanUpScene";')
            mel.eval('cleanUp_ShouldReportProgress;')
            mel.eval('performCleanUpScene;')
        return [missTex, objectsDict]

    def runCheckPreset(self, preset):
        result = []
        if preset == 'Modelling sCheck':
            result = self.sceneCheck(ref=True, cam=True, history=True, freezeTransf=True, nonStChannel=True, normal=True, UVs=True, polyCleanUp=True, shell=True, cleanUp=True)
        elif preset == 'Textures sCheck':
            result = self.sceneCheck(ref=True, cam=True, history=True, nonStChannel=True, normal=True, UVs=True, aiShader=True, texture=True, cleanUp=True)
        elif preset == 'Cloth&Hair sCheck':
            result = self.sceneCheck(ref=True, cam=True, normal=True, UVs=True, aiShader=True)
        elif preset == 'Rigging sCheck':
            result = self.sceneCheck(ref=True, cam=True, aiShader=True)
        return result