'''
Created on Sep 8, 2015

@author: qurban.ali
'''
import pymel.core as pc

class Mesh():
    OBJ_ID_ATTR_NAME = ''
    def __init__(self, mesh):
        self.mesh = mesh
    
    def getId(self):
        self.mesh.attr(self.__class__.OBJ_ID_ATTR_NAME).get()
    
    def setId(self, num):
        self.mesh.attr(self.__class__.OBJ_ID_ATTR_NAME).set(num)
        
    def getName(self):
        return self.mesh.name()
    
    def setName(self, name):
        pc.rename(self.mesh, name)
        
    def getAOV(self):
        pass

class AOV():
    AOV_TYPE_NAME = ''
    AOV_SUB_TYPE_NAME = ''
    AOV_CREATE_COMMAND = ''
    RED_ID_ATTR_NAME = ''
    GREEN_ID_ATTR_NAME = ''
    BLUE_ID_ATTR_NAME = ''

class Material():
    MATERIAL_TYPE_NAME = ''
    MATERIAL_ID_ATTR_NAME = ''
    
class MeshList(list):
    def __init__(self):
        super(MeshList, self).__init__()
        self._populate()
        
    def _populate(self):
        del self[:]
        for mesh in self._getMeshes():
            self.append(Mesh(mesh))
            
    def _getMeshes(self):
        chars = pc.ls('characters')
        if chars:
            return [x for x in chars.getChildren() if type(x) == pc.nt.Transform and x.getShapes(ni=True)]
        
    def getMeshesWithIds(self):
        return [x for x in self if x.getId() > 0]
    
    def getMeshesWithNoIds(self):
        return [x for x in self if x.getId() == 0]
    
class AOVList(list):
    TITLE = ''
    def __init__(self):
        super(AOVList, self).__init__()
        self._populate()
        
    def _populate(self):
        del self[:]
        for aov in self._getAOVs():
            self.append(AOV(aov))
            
    def _getAOVs(self):
        aovs = pc.ls(type=AOV.AOV_TYPE_NAME)
        if aovs:
            return [x for x in aovs]
    
def setMeshAttrs(attr):
    Mesh.OBJ_ID_ATTR_NAME = attr

def setAOVAttrs(atn, rian, gian, bian, title):
    AOV.AOV_TYPE_NAME = atn
    AOV.RED_ID_ATTR_NAME = rian
    AOV.GREEN_ID_ATTR_NAME = gian
    AOV.BLUE_ID_ATTR_NAME = bian
    AOVList.TITLE = title

def setMaterialAttrs(mtn, mian):
    Material.MATERIAL_TYPE_NAME = mtn
    Material.MATERIAL_ID_ATTR_NAME = mian
    
#meshList = MeshList()
#aovList = AOVList()
#materialList = MaterialList()