
import pymel.core as pc
from collections import OrderedDict
import json

import imaya

def getRenderLayerInfo(renderLayer):

    currentLayer = pc.editRenderLayerGlobals(q=1, crl=1)
    if currentLayer != renderLayer:
        pc.editRenderLayerGlobals(crl=renderLayer)

    info = OrderedDict()
    info['cameras'] = [str(cam) for cam in imaya.getCameras(True, False)]
    info['range']   = str(imaya.getFrameRange())
    info['passes']  = [str((str(aov), aov.attr('aovType').get()))
            for aov in pc.ls(type='RedshiftAOV')
            if aov.enabled.get()]
    info['resolution'] = str(imaya.getResolution())

    return info

def gatherRenderLayersInfo():
    currentLayer = pc.editRenderLayerGlobals(q=1, crl=1)
    layerInfo = OrderedDict()
    for crl in imaya.getRenderLayers():
        layerInfo[str(crl)]=getRenderLayerInfo(crl)
    pc.editRenderLayerGlobals(crl=currentLayer)
    return layerInfo

def displayRenderLayersInfo():
    if pc.window('RenderLayerInfo', exists=True ):
        pc.deleteUI('RenderLayerInfo')
    with pc.window('RenderLayerInfo', wh=(300, 700)) as win:
        with pc.paneLayout() as pl:
            info = gatherRenderLayersInfo()
            data = json.dumps(info, indent=4)
            lines = data.splitlines(False)
            pc.textScrollList(allowMultiSelection=True, append=lines )
    win.show()

if __name__ == '__main__':
    displayRenderLayersInfo()

