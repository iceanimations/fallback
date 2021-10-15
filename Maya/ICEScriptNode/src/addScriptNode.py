'''
Created on Jan 20, 2015

@author: qurban.ali
'''
import pymel.core as pc
import maya.cmds as mc
import appUsageApp

__NODE_NAME__ = 'ICE_SCRIPT_NODE'

__SCRIPT__ = '''
import pymel.core as pc
for refNode in pc.ls(type=pc.nt.Reference):
    try:
        fNode = pc.FileReference(refNode)
        if fNode.isLoaded():
            fNode.load()
            
    except:
        pass
for node in pc.ls(type=pc.nt.File):
        node.fileTextureName.set(node.fileTextureName.get().replace('\\\\', '/'))
'''

def addNode():
    '''adds a script node to the scene, to run some script at scene open time'''
    
    # check if it already exists
    for node in pc.ls(type=pc.nt.Script):
        if node.name().split(':')[-1].split('|')[-1] == __NODE_NAME__:
            return
    # fix the problem now
    exec(__SCRIPT__)
    # fix for the future
    pc.scriptNode(st=1, bs=__SCRIPT__, n=__NODE_NAME__, stp='python')
    
    pc.inViewMessage(amg='<hl>Textures fixed successfully</hl>', pos='midCenter', fade=True )
    
    appUsageApp.updateDatabase('FixRedshiftTextures')