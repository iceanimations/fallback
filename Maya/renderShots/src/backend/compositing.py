'''
Created on Aug 6, 2015

@author: qurban.ali
'''
import sys
import nuke
import nukescripts
import os
osp = os.path
import shutil
import re

#homeDir = osp.join(osp.expanduser('~'), 'render_shots')

def createNode(nodeName):
    node = nuke.createNode(nodeName)
    nukescripts.clear_selection_recursive()
    node.setSelected(True)
    return node
    
def createReadNode(nodes, layerName):
    for node in nodes:
        if node.name().lower().startswith(layerName):
            node.knob('on_error').setValue(1)
            node.setSelected(True)
            return node

def getFrameRange(nodes):
    frameRange = []
    for node in nodes:
        fr = range(int(node.knob('first').getValue()), int(node.knob('last').getValue()) + 1)
        if len(fr) > len(frameRange):
            frameRange = fr
    return min(frameRange), max(frameRange)

def createComp(allFrames, shots):
    
    compPath = osp.join(homeDir, 'comps')
    if not osp.exists(compPath):
        os.mkdir(compPath)
    
    for phile in os.listdir(compPath):
        filePath = osp.join(compPath, phile)
        if osp.isfile(filePath):
            try:
                os.remove(filePath)
            except:
                pass
        elif osp.isdir(filePath):
            try:
                shutil.rmtree(filePath)
            except:
                pass
    
    rendersPath = osp.join(compPath, 'renders')
    if not osp.exists(rendersPath):
        os.mkdir(rendersPath)
    seqPath = allFrames if allFrames else homeDir
    errors = {}
    for shot in shots:
        try:
            shotPath = osp.join(seqPath, shot)
            if not osp.exists(shotPath): continue
            if allFrames:
                shotPath = osp.join(shotPath, os.listdir(shotPath)[0])
            layers = os.listdir(shotPath)
            nodes = []
            frames = []
            if layers:
                for layer in layers:
                    layerPath = osp.join(shotPath, layer)
                    if osp.isfile(layerPath): continue
                    for aov in os.listdir(layerPath):
                        if aov.lower().endswith('beauty'):
                            node = nuke.createNode('Read')
                            aovPath = osp.join(layerPath, aov)
                            if osp.isfile(aovPath): continue
                            filenames = os.listdir(aovPath)
                            if filenames:
                                match = re.search('\.\d+\.', filenames[0])
                                if match:
                                    padding = 1
                                    if allFrames:
                                        padding = len(match.group()) - 2
                                    frames = [int(re.search('\.\d+\.', phile).group()[1:-1]) for phile in filenames]
                                    frames = sorted(frames)
                                    if not allFrames: # if .mov not needed
                                        for i, frame in enumerate(frames):
                                            for phile in filenames:
                                                if str(frame) in phile:
                                                    try:
                                                        os.rename(osp.join(aovPath, phile), osp.join(aovPath, re.sub('\.\d+\.', '.'+str(i+1)+'.', phile)))
                                                    except:
                                                        pass
                                        frames = [1, 2, 3]
                                    padding = '#'* padding
                                    node.knob('file').setValue(osp.join(aovPath, re.sub('\.\d+\.', '.'+ padding +'.', filenames[0])).replace('\\', '/'))
                                    node.knob('first').setValue(min(frames)); node.knob('origfirst').setValue(min(frames))
                                    node.knob('last').setValue(max(frames)); node.knob('origlast').setValue(max(frames))
                                    
                                    node.setName(layer)
                                    nodes.append(node)
            print nodes
            if nodes:
                nukescripts.clear_selection_recursive()
                createReadNode(nodes, 'occ')
                envOccNode = createReadNode(nodes, 'env_occ')
                envNode = createReadNode(nodes, 'env')
                if envNode: envNode.knob('on_error').setValue(3)
                if len(nuke.selectedNodes()) == 2:
                    node = createNode('Merge2').knob('operation')
                    if envOccNode is not None:
                        node.setValue(20)
                try:
                    lastNode = nuke.selectedNode()
                except:
                    lastNode = None
                nukescripts.clear_selection_recursive()
                createReadNode(nodes, 'cont')
                if lastNode: lastNode.setSelected(True)
                try:
                    if len(nuke.selectedNodes()) == 2:
                        mNode = createNode('Merge2')
                        mNode.knob('operation').setValue(20)
                        mNode.knob('screen_alpha').setValue(1)
                    lastNode = nuke.selectedNode()
                    nukescripts.clear_selection_recursive()
                except:
                    pass
                nukescripts.clear_selection_recursive()
                createReadNode(nodes, 'reflection')
                if lastNode: lastNode.setSelected(True)
                try:
                    if len(nuke.selectedNodes()) == 2:
                        createNode('Merge2')
                    lastNode = nuke.selectedNode()
                    nukescripts.clear_selection_recursive()
                except:
                    pass

                nukescripts.clear_selection_recursive()
                createReadNode(nodes, 'shadow')
                if lastNode: lastNode.setSelected(True)
                try:
                    if len(nuke.selectedNodes()) == 2:
                        createNode('Merge2').knob('mix').setValue(0.5)
                    lastNode = nuke.selectedNode()
                    nukescripts.clear_selection_recursive()
                except:
                    pass
                nukescripts.clear_selection_recursive()
                createReadNode(nodes, 'gen')
                if lastNode: lastNode.setSelected(True)
                try:
                    if len(nuke.selectedNodes()) == 2:
                        createNode('Merge2')
                    lastNode = nuke.selectedNode()
                    nukescripts.clear_selection_recursive()
                except: pass
                nukescripts.clear_selection_recursive()
                if lastNode: lastNode.setSelected(True)
                createReadNode(nodes, 'char')
                try:
                    if len(nuke.selectedNodes()) == 2:
                        createNode('Merge2').knob('operation').setValue(28)
                        lastNode = nuke.selectedNode()
                        nukescripts.clear_selection_recursive()
                except:
                    pass
                if lastNode: lastNode.setSelected(True)
                try:
                    if len(nuke.selectedNodes()) == 2:
                        createNode('Merge2')
                except:
                    return
                writeNode = nuke.createNode('Write')
                renderShotDir = osp.join(rendersPath, shot)
                if not osp.exists(renderShotDir):
                    os.mkdir(renderShotDir)
                writeNode.knob('file').setValue(osp.join(renderShotDir, shot +'.#####.jpg').replace('\\', '/'))
                nuke.scriptSaveAs(osp.join(compPath, shot+'.nk'), 1)
                minFrame = 1; maxFrame = 3
                if frames and allFrames:
                    minFrame, maxFrame = getFrameRange(nodes)
                nuke.execute(writeNode, minFrame, maxFrame, continueOnError=True)
            nuke.scriptClose()
        except Exception as ex:
            errors[shot] = str(ex)
    with open(osp.join(osp.expanduser('~'), 'compositing', 'errors.txt'), 'w') as f:
        f.write(str(errors))

if __name__ == "__main__":
    shots = None
    try:
        with open(osp.join(osp.expanduser('~'), 'compositing', 'info.txt')) as f:
            shots = eval(f.read())
        if shots:
            homeDir = shots[1]
            createComp(shots[0], shots[2:])
    except Exception as ex:
        with open(osp.join(osp.expanduser('~'), 'compositing', 'errors.txt'), 'w') as f:
            f.write(str({'Unknown': str(ex)}))