'''
Created on Sep 8, 2015

@author: qurban.ali
'''
import pymel.core as pc
import utilities as utils

#mtls = ['RedshiftArchitectural']
matteIdsMaterialsSetName = 'matte_ids_materials'

def getAOVs(obj=False, mtl=False):
    return [aov for aov in pc.ls(type='RedshiftAOV')
            if aov.aovType.get() == 'Puzzle Matte'
            and ((obj and aov.mode.get() == 1)
                 or (mtl and aov.mode.get() == 0))]

def getMeshesFromAOV(aov):
    '''returns meshes assigned to given aov'''
    aov = pc.PyNode(aov)
    meshes = {}
    for aovId in ['redId', 'greenId', 'blueId']:
        meshes[aovId] = []
        for mesh in utils.getMeshes():
            meshId = mesh.rsObjectId.get()
            if meshId > 0 and meshId == pc.getAttr('.'.join([aov.name(), aovId])):
                meshes[aovId].append(mesh.name())
    return meshes

def getMtlsFromAOV(aov):
    '''returns materials assigned to given aov'''
    aov = pc.PyNode(aov)
    mtls = {}
    for aovId in ['redId', 'greenId', 'blueId']:
        mtls[aovId] = []
        for mtl in getMtls():
            try:
                mtlId = mtl.future(type='shadingEngine')[0].rsMaterialId.get()
            except IndexError:
                continue
            if mtlId > 0 and mtlId == pc.getAttr('.'.join([aov.name(), aovId])):
                    mtls[aovId].append(mtl.name())
    return mtls

def getMtlsFromMeshes(meshes):
    mtls = []
    for mesh in meshes:
            shape = mesh.getShape(ni=True)
            if shape:
                for sg in set(pc.listConnections(shape, type=pc.nt.ShadingEngine)):
                    for mtl in sg.surfaceShader.inputs():
                        mtls.append(mtl.name())
    return mtls

def getSelectedMtls():
    mtls = [mtl.name() for mtl in pc.ls(sl=True, type=[pc.nt.RedshiftArchitectural, pc.nt.RedshiftMaterialBlender])]
    mtls.extend(getMtlsFromMeshes([mesh.firstParent() for mesh in pc.ls(sl=True, type='mesh', dag=True)]))
    mtls = [mtl for mtl in mtls if type(pc.PyNode(mtl).outColor.outputs()[0]) != pc.nt.RedshiftMaterialBlender]
    return mtls

def getUnassignedMeshes():
    meshes = []
    for mesh in utils.getMeshes():
        if mesh.rsObjectId.get() == 0 or mesh.rsObjectId.get() not in getAOVIds(obj=True):
            meshes.append(mesh.name())
    return meshes

def getUnassignedMaterials():
    mtls = []
    for mtl in getMtls():
        try:
            mtlId = mtl.future(type='shadingEngine')[0].rsMaterialId.get()
        except IndexError:
            continue
        if mtlId == 0 or mtlId not in getAOVIds(mtl=True):
            mtls.append(mtl.name())
    return mtls

def getMtls():
    mtlSet = pc.ls(matteIdsMaterialsSetName)
    if mtlSet:
        return mtlSet[0].members()
    else:
        return []

def getAOVIds(**kwargs):
    aovs = getAOVs(**kwargs)
    ids = []
    for aov in aovs:
        ids.extend([aov.redId.get(), aov.greenId.get(), aov.blueId.get()])
    return sorted(list(set(ids)))

def getLowestUniqueId(**kwargs):
    ids = getAOVIds(**kwargs)
    return [x for x in range(1, max(ids) + 2) if x not in ids][0]
        

def colToAttr(col):
    return {1: 'redId', 2: 'greenId', 3: 'blueId'}.get(col)

def removeObjectId(obj):
    obj = pc.PyNode(obj)
    obj.rsObjectId.set(0)

def addObjectId(aov, obj, col):
    obj = pc.PyNode(obj)
    aov = pc.PyNode(aov)
    attr = pc.PyNode('.'.join([aov.name(), colToAttr(col)]))
    if attr.get() == 0:
        attr.set(getLowestUniqueId(obj=True))
    obj.rsObjectId.set(attr.get())

def removeMtlId(mtl):
    mtl = pc.PyNode(mtl)
    for sg in mtl.future(type='shadingEngine'):
        sg.rsMaterialId.set(0)

def addMtlId(aov, mtl, col):
    aov = pc.PyNode(aov)
    mtl = pc.PyNode(mtl)
    attr = pc.PyNode('.'.join([aov.name(), colToAttr(col)]))
    if attr.get() == 0:
        attr.set(getLowestUniqueId(mtl=True))
    for sg in mtl.future(type='shadingEngine'):
        sg.rsMaterialId.set(attr.get())
        
def addMtlsToSet(mtls):
    mtlSet = pc.ls(matteIdsMaterialsSetName)
    if mtlSet:
        pc.sets(mtlSet[0], e=True, fe=mtls)
    else:
        sl = pc.ls(sl=True)
        pc.select(mtls)
        pc.sets(name=matteIdsMaterialsSetName)
        pc.select(sl)