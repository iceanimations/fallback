import pymel.core as pc
import utilities as util

def transfer_shaders(src_mesh, targ):
    '''accepts two mesh nodes and transfers shaders from first one to the second one'''
    # list the shading engines connected to the source mesh
    shGroups = set(pc.listConnections(src_mesh, type='shadingEngine'))
    for sg in shGroups:
        # get the polygons and meshes on which the 'sg' is applied
        sgMembers = pc.sets(sg, q = True)
        # when only single sg is applied on whole mesh
        if sgMembers:
            flag = False
            for member in sgMembers:
                if src_mesh == member:
                    flag = True
                    break
            if flag:
                pc.sets( sg, fe = targ)
            # when different sgs are applied on single mesh
            else:
                for f in sgMembers:
                    if f.node() != src_mesh: continue
                    index = '.' + f.split('.')[-1]
                    pc.sets( sg, fe = targ + index)

def main(sourceSet, targetSets, transferUVs):
    '''accpts two sets and gets the meshes from those sets'''
    
    sourceSet = pc.PyNode(sourceSet)
    badFaces = {} # when the number of faces is is different in the source and target meshes
    badLength = [] # when the number of meshes is different in the source and target sets
    sourceMeshes = []
    for transform in sourceSet:
        mesh = transform.getShape()
        if type(mesh) == pc.nt.Mesh: sourceMeshes.append(mesh)
    sourceLength = len(sourceMeshes)
    
    for _set in targetSets:
        _set = pc.PyNode(_set)
        targetMeshes = []    
        #get the meshes from the transform nodes
        for transform in _set:
            mesh = transform.getShape()
            if type(mesh) ==  pc.nt.Mesh: targetMeshes.append(mesh)
        # for each mesh in source set, transfer the shader to corresponding mesh in the target set
        for i in range(sourceLength):
            src = sourceMeshes[i]
            # get the post fix name of the mesh in the set
            srcPostFix = src.split('|')[-1].split(':')[-1]
            targetPostFixs = [x.split('|')[-1].split(':')[-1] for x in targetMeshes]
            for postFix in targetPostFixs:
                index = None
                if srcPostFix == postFix:
                    index = targetPostFixs.index(postFix)
                    break
            if index is not None:
                targ = targetMeshes[index]
                # check if the number of faces is different in the corresponding meshes
                if len(src.faces) != len(targ.faces):
                    badFaces[src] = targ
                    continue
                #transfer the shaders
                transfer_shaders(src, targ)
                #transfer the UVs
                if transferUVs:
                    util.transferUVs(src, targ)
            else: badLength.append(src)
    return badFaces, badLength