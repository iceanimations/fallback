'''
Created on Feb 9, 2015

@author: qurban.ali
'''
import pymel.core as pc
nt = pc.nt
import appUsageApp

_script = '''
import pymel.core as pc
nt = pc.nt
for sg in pc.ls(type=pc.nt.ShadingEngine):
    if pc.attributeQuery('objs', node=sg, exists=True):
        print 'putting', sg.objs.get()
        pc.sets(sg, e=True, fe=eval(sg.objs.get()))
'''

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
        #pc.inViewMessage(amg='<hl>SG nodes selected (%s)</hl>'%str(len(sgs)), pos='midCenter', fade=True )
    return True

def _addAttr():
    if not _select():
        return
    sgs = pc.ls(sl=True, type='shadingEngine')
    if not sgs:
        pc.inViewMessage(amg='<hl>No SG node selected in the scene', pos='midCenter', fade=True )
        return
    for node in sgs:
        objects = pc.sets(node, q=True)
        objects = [obj.name() for obj in objects]
        try:
            pc.addAttr(node, sn='objs', ln='objects', hidden=True, dt="string")
        except:
            pass
        print 'adding', objects
        node.objs.set(str(objects))

    if not 'ICE_SG_SOLVER' in [script.name() for script in pc.ls(type='script')]:
        pc.scriptNode(n='ICE_SG_SOLVER', st=1, bs=_script, stp='python')
        
    pc.inViewMessage(amg='<hl>SG nodes setup ready (%s)</hl>'%str(len(sgs)), pos='midCenter', fade=True )
    
    appUsageApp.updateDatabase('setupSGNodes')