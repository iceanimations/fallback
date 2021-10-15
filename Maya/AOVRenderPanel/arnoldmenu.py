# pieces of code picked up from
# http://therenderblog.com/loading-render-passesaovs-inside-maya-renderview-with-python/

import os
import pymel.core as pc
import maya.cmds as cmds
op = os.path

def aovUI():

    aovsList = cmds.optionMenu('com_iceanimations_arnold_aovs',
            w = 125, h = 26, label = 'AOV',
            cc = loadAOV, p = 'renderViewToolbar')
    # camList = cmds.optionMenu('com_iceanimations_cameras',
    #                           w = 125, h = 26, label = 'Camera',
    #                           cc = loadAOV, p = 'renderViewToolbar')

    activeAOVS = pc.ls(et='aiAOV')
    aovsNames = ['beauty'] + sorted(list(set([i.getAttr("name") for i in activeAOVS])))
    # cams = sorted(pc.ls(type = 'camera'))

    for i, item in enumerate(aovsNames):
        cmds.menuItem(label=item, p = aovsList)
        if item == pc.getAttr("defaultArnoldRenderOptions.displayAOV"):
            cmds.optionMenu('com_iceanimations_arnold_aovs', edit = True, select = i + 1)

    # for i, item in enumerate(cams):
    #     cmds.menuItem(label=str(item.firstParent()), p = camList)

def loadAOV(*args):

    activeAOVS = cmds.ls(et='aiAOV')
    aovsNames = [i.split('_', 1)[1] for i in activeAOVS]

    if activeAOVS == []:
        cmds.warning("No aov's setup")
    else:

        rview = cmds.getPanel( sty = 'renderWindowPanel' )
        selectedAOV = cmds.optionMenu('com_iceanimations_arnold_aovs',q=1,v=1)
        camera = pc.mel.getCurrentCamera()
        pc.setAttr("defaultArnoldRenderOptions.displayAOV", selectedAOV)

        img = pc.renderSettings(fin = True, lut = True, fpt = True,
                cam = camera)[0]
        if '<RenderPass>' not in img:
            gin = pc.renderSettings(gin = 1, lut =1, cam = camera)[0]
            gin = gin[1:] if gin[0] == "/" else gin
            imgTillTmp = img[:img.find(gin)]
            img = op.join(imgTillTmp, selectedAOV, gin)
        pathToImg = img.replace('<RenderPass>', selectedAOV)
        print pathToImg
        cmds.renderWindowEditor(rview, e=True, li=pathToImg)

def drawMenu():
    if pc.mel.currentRenderer().lower() != "arnold":
        return False

    currentAOV = pc.getAttr("defaultArnoldRenderOptions.displayAOV")

    aovUI()

drawMenu()
