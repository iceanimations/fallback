'''
Created on Apr 8, 2014

@author: qurban.ali
'''

import pymel.core as pc
import appUsageApp

def doTheMagic():
    try:
        redshifts = pc.ls(sl=True, type=pc.nt.RedshiftArchitectural)
        print redshifts
    except AttributeError:
        pc.confirmDialog(title="Error", message="It seems like Redshift is not loaded or installed", button="Ok")
        return
    if not redshifts:
        pc.confirmDialog(title="Error", message="No selection found in the scene", button="Ok")
        return
    occ = pc.shadingNode(pc.nt.RedshiftAmbientOcclusion, asShader=1)
    for aiSh in redshifts:
        for sg in pc.listConnections(aiSh, type='shadingEngine'):
            try:
                pc.editRenderLayerAdjustment(sg.rsSurfaceShader)
            except Exception, ex:
                pc.confirmDialog(title="Error", message=str(ex), button="Ok")
                pc.delete(occ)
                return
            occ.outColor.connect(sg.rsSurfaceShader, f=True)
        pc.rename(occ, '_'.join([aiSh.name().split(':')[-1].split('|')[-1], 'rsAmbientOcclusion']))

    appUsageApp.updateDatabase('AmbientOcclusion')