import sys
sys.path.extend([r"R:\Pipe_Repo\Users\Hussain\utilities\loader\command\python",
                 r"R:\Pipe_Repo\Projects\TACTIC"])
import RedshiftAOVTools
import os.path as osp
import pymel.core as pc
import imaya
reload(imaya)

homeDir = osp.join(osp.expanduser('~'), 'render_shots')

def configureScene(parent=None, renderScene=False, resolution=None, shot=None):
    if not shot:
        f = open(osp.join(homeDir, 'info.txt'))
        shot = f.read()
        f.close()
    pc.workspace(homeDir, o=True)
    node = pc.PyNode('redshiftOptions')
    
    node.imageFilePrefix.set("%s\<RenderLayer>\<RenderLayer>_<AOV>\<RenderLayer>_<AOV>_"%shot)
    pc.setAttr("defaultRenderGlobals.imageFilePrefix", "%s/<RenderLayer>/<RenderLayer>_<AOV>/<RenderLayer>_<AOV>_"%shot, type="string")
    RedshiftAOVTools.fixAOVPrefixes()
    
    try:
        for aov in pc.ls(type=pc.nt.RedshiftAOV):
            aov.filePrefix.set(aov.filePrefix.get().replace('<Camera>', shot))
    except AttributeError:
        if parent:
            parent.showMessage(msg='It seems like Redshift is not installed or not loaded')
        else:
            print 'It seems like Redshift is not installed or not loaded'
        return
    pc.setAttr('defaultRenderGlobals.animation', 1)
    pc.setAttr('defaultResolution.width', int(resolution[0]))
    pc.setAttr('defaultResolution.height', int(resolution[1]))
    pc.setAttr('defaultResolution.deviceAspectRatio', float(resolution[2]))

    minTime = pc.playbackOptions(q=True, minTime=True)
    maxTime = pc.playbackOptions(q=True, maxTime=True)
    diff = maxTime - minTime
    step = diff/2.0
    # configure frame range for each layer
    for layer in imaya.getRenderLayers():
        pc.editRenderLayerGlobals(currentRenderLayer=layer)
        pc.setAttr('defaultRenderGlobals.startFrame', minTime)
        pc.setAttr('defaultRenderGlobals.endFrame', maxTime)
        pc.setAttr('defaultRenderGlobals.byFrameStep', step)

    if diff%2 != 0:
        step += 0.5
    frames = [int(minTime), int(minTime + step), int(maxTime)]
    with open(osp.join(homeDir, 'info1.txt'), 'w') as f:
        f.write(str(frames))
    if renderScene:
        layers = imaya.batchRender()
        for layer in layers:
            print 'Rendering: %s'%layer
        for layer in layers:
            layer.renderable.set(1)
    return frames