'''
Created on Apr 8, 2014

@author: qurban.ali
'''

import pymel.core as pc
import site
site.addsitedir(r'R:\Pipe_Repo\Users\Qurban\utilities')
import appUsageApp

def getFlatDiffuseIndex(sg):
    for i in sg.aiCustomAOVs.getArrayIndices():
        if 'flat_diffuse' in sg.aiCustomAOVs[i].get():
            return i

def doTheMagic():
    try:
        arnolds = pc.ls(sl=True, type=pc.nt.AiStandard)
    except AttributeError:
        pc.confirmDialog(title="Error", message="It seems like Arnold is not loaded or installed", button="Ok")
        return
    if not arnolds:
        pc.confirmDialog(title="Error", message="No selection found in the scene", button="Ok")
        return
    try:
        value = getFlatDiffuseIndex(pc.ls(type=pc.nt.ShadingEngine)[0])
        if value is not None:
            pass
        else:
            pc.confirmDialog(title="Error", message="No AOV named \"flat_diffuse\" found in the scene", button="Ok")
            return
    except IndexError:
        pc.confirmDialog(title="Error", message="No Shading engine found in the scene", button="Ok")
        return
    for aiSh in arnolds:
        aiUtility = pc.shadingNode(pc.nt.AiUtility, asShader=1)
        for sg in pc.listConnections(aiSh, type='shadingEngine'):
            aiUtility.outColor.connect(sg.aiCustomAOVs[getFlatDiffuseIndex(sg)].aovInput, f=True)
        try:
            aiSh.color.inputs(plugs=True)[0].connect(aiUtility.color, f=True)
        except IndexError:
            aiUtility.color.set(aiSh.color.get())
        try:
            aiSh.opacity.inputs()[0].outAlpha.connect(aiUtility.opacity, f=True)
        except IndexError:
            aiUtility.opacity.set(aiSh.opacity.get())
        aiUtility.shadeMode.set(2)
        pc.rename(aiUtility, '_'.join([aiSh.name().split(':')[-1].split('|')[-1], 'aiUtility']))

    appUsageApp.updateDatabase('AddAiUtility')