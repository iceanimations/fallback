'''
Created on Feb 9, 2015

@author: qurban.ali
'''
import pymel.core as pc

def _select():
    meshes = pc.ls(type='mesh', sl=True, dag=True)
    if not meshes:
        pc.inViewMessage(amg='<hl>No mesh selected in the scene', pos='midCenter', fade=True )
        return
    sgs = set()
    for mesh in meshes:
        sgs.update(set(pc.listConnections(mesh, type='shadingEngine')))
    if sgs:
        pc.select(list(sgs), ne=True)
        pc.inViewMessage(amg='<hl>SG nodes selected (%s)</hl>'%str(len(sgs)), pos='midCenter', fade=True )