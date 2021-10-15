'''
Created on Aug 29, 2014

@author: qurban.ali
'''
import pymel.core as pc

def assign():
    
    groups = pc.ls(sl=True, type=pc.nt.Transform)
    if not groups:
        pc.warning('No group selected...')
    for grp in groups:
        for transform in grp.getChildren():
            name = transform.name().split('|')[-1].split(':')[-1]
            aicmd = 'createRenderNodeCB -asShader "surfaceShader" aiStandard ""'
            try:
                arnold = pc.PyNode(pc.Mel.eval(aicmd))
            except:
                pc.warning("Seems like Arnod is either not installed or not loaded")
                return
            sg = arnold.outColor.outputs()[0]
            pc.sets(sg, fe=transform.getShape())
            
            pc.rename(sg, sg.name().replace(arnold.name(), name))
            pc.rename(arnold, name +'_shader')