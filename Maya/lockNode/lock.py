'''
Locks and unlocks the selected meshe(s)
Author: Qurban Ali (qurban.ali@iceanimations.com)
'''

import pymel.core as pc

# update the database, how many times this app is used
import site
site.addsitedir(r'r:/pipe_repo/users/qurban')
import appUsageApp
appUsageApp.updateDatabase('lockNode')
#/////////////////////////////////////////////////////

def gui():
    with pc.window('lock/unlock mesh', wh = (200, 50)) as win:
        with pc.rowLayout(numberOfColumns = 2, columnAttach2 = ('both', 'both')):
            btn1 = pc.button(label = 'Lock', w = 100)
            btn1.setCommand(pc.Callback(getSelection, btn1))
            btn2 = pc.button(label = 'Unlock', w = 100)
            btn2.setCommand(pc.Callback(getSelection, btn2))
    win.setResizeToFitChildren(1)

def getSelection(btn):
    meshes = pc.ls(sl = True)
    if meshes:
        text = btn.getLabel()
        if text == 'Lock':
            lockNode(meshes)
        elif text == 'Unlock':
            unlockNode(meshes)
        else: pass
    else:
        pc.warning('No mesh is currently selected...')
        return

def lockNode(meshes):
    for mesh in meshes: 
        mesh.t.setLocked(True)
        mesh.r.setLocked(True)
        mesh.s.setLocked(True)
        pc.lockNode(mesh, lock = True)
        

def unlockNode(meshes):
    for mesh in meshes:
        pc.lockNode(mesh, lock = False)
        mesh.t.setLocked(False)
        mesh.r.setLocked(False)
        mesh.s.setLocked(False)

def main():
    gui()