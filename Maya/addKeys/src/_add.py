'''
Created on Jul 6, 2015

@author: qurban.ali
'''
import pymel.core as pc
import appUsageApp

def add(sel=None, minTime=None, maxTime=None, removeExisting=True):
    if not sel:
        sel = pc.ls(sl=True)
        if not sel:
            pc.warning('No selection found in the scene')
            return
    if not minTime and not maxTime:
        minTime = pc.playbackOptions(minTime=True, q=True)
        maxTime = pc.playbackOptions(maxTime=True, q=True)
    
    for obj in sel:
        try:
            pc.select(obj)
            if removeExisting:
                pc.mel.eval('cutKey -clear -time ":" -hierarchy none -controlPoints 0 -shape 1 {"%s"};'%obj.name())
            pc.mel.eval('setKeyframe -breakdown 0 -hierarchy none -controlPoints 0 -shape 0 -time %s {"%s"};'%(minTime,obj.name()))
            pc.mel.eval('setKeyframe -breakdown 0 -hierarchy none -controlPoints 0 -shape 0 -time %s {"%s"};'%(maxTime,obj.name()))
            if obj.hasAttr('in'): obj.attr('in').set(minTime)
            if obj.hasAttr('out'): obj.out.set(maxTime)
        except Exception as ex:
            pc.warning(str(ex))
    
    appUsageApp.updateDatabase('addKeys')