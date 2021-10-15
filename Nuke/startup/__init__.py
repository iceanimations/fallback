import functools
import nuke

import addWrite


openLoc = '''
import subprocess
import os.path as osp
import nuke
subprocess.call(
    'explorer '+
    osp.normpath(osp.dirname(nuke.thisNode().knob('file').getValue())))
'''


def readNode():
    node = nuke.thisNode()
    knobName = 'openLoc'
    if knobName not in nuke.Node.knobs(node):
        node.addKnob(nuke.PyScript_Knob(knobName, 'Open Location', openLoc))


def writeNode():
    node = nuke.thisNode()
    knobName = 'openLoc'
    if knobName not in nuke.Node.knobs(node):
        node.addKnob(nuke.PyScript_Knob(knobName, 'Open Location', openLoc))


def archiveOutput():
    node = nuke.thisNode()
    addWrite.addArchiveKnobs(node)


def setupNuke():
    nuke.addOnCreate(readNode, nodeClass='Read')
    nuke.addOnCreate(writeNode, nodeClass='Write')
    nuke.addOnCreate(archiveOutput, nodeClass='Write')


def getBackdrop(node=None):
    if node is None:
        node = nuke.selectedNode()
    if node:
        bds = nuke.allNodes('BackdropNode')
        if bds:
            for bd in bds:
                if node in activateBackdrop(bd, False):
                    return bd


def activateBackdrop(node, select=True):
    nodes = []
    xmin = node.knob('xpos').value()
    xmax = xmin + node.knob('bdwidth').value()
    ymin = node.knob('ypos').value()
    ymax = ymin + node.knob('bdheight').value()
    node.knob('selected').setValue(True)
    for i in [i for i in nuke.allNodes() if i is not node]:
        ixmin = i.knob('xpos').value()
        ixmax = ixmin + i.screenWidth()
        iymin = i.knob('ypos').value()
        iymax = iymin + i.screenHeight()
        if ((ixmin >= xmin and ixmax < xmax) and
                (iymin >= ymin and iymax < ymax)):
            nodes.append(i)
            if select:
                i.knob('selected').setValue(True)
            else:
                node.setSelected(False)
    return nodes


nuke.getBackdrop = getBackdrop
nuke.activateBackdrop = activateBackdrop
nuke.getBackdropNodes = functools.partial(activateBackdrop, select=False)
