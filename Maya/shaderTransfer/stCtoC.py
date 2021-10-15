import pymel.core as pc
import maya.cmds as mc
import utilities as util

def transfer_shaders(src_mesh, targ):
    # list the shading engines connected to the source mesh
    listOfShaders = pc.listConnections(src_mesh, type='shadingEngine')
    shGroups = set()
    for shader in listOfShaders:
        shGroups.add(str(shader)) 
    for sg in shGroups:
        print 'sg: ', sg
        sgMembers = mc.sets(sg, q = True)
        print 'sgMembers: ', sgMembers
        if sgMembers:
            for mem in sgMembers:
                if mem == src_mesh:
                    pc.sets(sg, e = 1, fe = targ)
                    return
            for mem in sgMembers:
                meshAndFace = mem.split('.')
                if len(meshAndFace) == 1:
                    pass
                else:
                    try:
                        if pc.PyNode(mem).node() == src_mesh:
                            face = meshAndFace[-1]
                            tar = '.'.join([str(targ), face])
                            pc.sets(pc.PyNode(sg), e=1, fe=pc.PyNode(tar))
                    except: pass

def main(source, target, transferUVs):
    badFaces = {}
    sourceMesh = pc.PyNode(source)
    if type(sourceMesh) == pc.nt.Transform:
        sourceMesh = sourceMesh.getShape()
    sourceFaces = sourceMesh.faces
    for transform in target:
        targetMesh = pc.PyNode(transform)
        if type(targetMesh) == pc.nt.Transform:
            targetMesh = targetMesh.getShape()
        targetFaces = targetMesh.faces
        if sourceFaces != targetFaces:
            badFaces[sourceMesh] = targetMesh
            continue
        #transfer the shaders
        transfer_shaders(sourceMesh, targetMesh)
        # transfer the UVs
        if transferUVs:
            util.transferUVs(sourceMesh, targetMesh)
    return badFaces