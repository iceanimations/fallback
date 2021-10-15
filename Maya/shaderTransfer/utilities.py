import pymel.core as pc

def isSelected():
    '''
    @return True, if selection exists in the current scene
    '''
    if pc.ls(sl = True): return True
    return False
    
def selectedObjects(policy):
    '''returns the list of selected objects from the scene'''
    objs = pc.ls(sl = True)
    if policy == 'stos':
        nativeType = pc.nt.ObjectSet
    if policy == 'ctoc':
        nativeType = pc.nt.Transform
    #check if all the selected objects are of required type
    for obj in objs:
        if type(obj) != nativeType:
            objs = []
            break
    return [str(obj) for obj in objs]

def transferUVs(source, target):
    '''
    transfers uv from source mesh to target mesh
    '''
    pc.polyTransfer(target, ao = source)