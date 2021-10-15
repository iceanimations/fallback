import pymel.core as pc
import maya.cmds as cmds

def translateToCorrectNode(i):
    pass
class Material():
    def __init__(self):
        self.currentFace = 0
        self.lastFace = 0
        self.lastMeshFaces = 0
    def transfer_shaders(self, meshes = []):
        '''
            This function transfers shaders from one mesh
            to other meshes of same geomatry. This function can work
            for polygonal meshes.
            This function transfers the shaders of combined mesh to separated mesh
        
            @params: list of two meshes, 1st one is source and
                     2nd one is target mesh
        '''
        src_mesh = meshes[0].getShape()
        # list the shading engines connected to the source mesh
        shGroups = set(pc.listConnections(src_mesh, type='shadingEngine'))
        # get the shape node of target mesh
        targ = meshes[1].getShape()
        for sg in shGroups:
            sg = str(sg)
            sgMembers = cmds.sets(sg, q = True)
            sgMembers = set(pc.ls(sgMembers, fl = True))
            if src_mesh in sgMembers:
                pc.sets(pc.PyNode(sg), fe = targ)
            else:
                for f in range(self.lastFace, self.currentFace + 1):
                    if cmds.sets(src_mesh + '.f[' + str(f) + ']', im = sg):
                        pc.sets(sg, fe = targ.f[f - self.lastMeshFaces])
        self.lastFace = self.currentFace + 1
        self.lastMeshFaces += self.no_of_faces
    def setMeshes(self):
        shaded = []
        un_shaded = []
        # get all the meshes
        meshes = pc.ls(sl = True)
        no_of_meshes = len(meshes)
        if not no_of_meshes:
            pc.error('Please select two objects from the scene')
            return
        num = 1
        for j in range(1, no_of_meshes):
            if j > 1:
                num = 0
            self.no_of_faces = pc.polyEvaluate(meshes[j], f = True)
            self.currentFace += self.no_of_faces - num
            self.transfer_shaders([meshes[0], meshes[j]])

def createClass():
    global mat
    mat = Material()
    mat.setMeshes()