'''
Created on Aug 1, 2015

@author: qurban.ali
'''
import os
osp = os.path
import subprocess
import re
import iutil

try:
    import renderer
    reload(renderer)
    homeDir = renderer.homeDir
except:
    pass
compPath = osp.join(homeDir, 'comps')
if not osp.exists(compPath):
    os.mkdir(compPath)
    
compositingDir = osp.join(osp.expanduser('~'), 'compositing')
if not osp.exists(compositingDir):
    os.mkdir(compositingDir)

compositingFile = osp.join(osp.dirname(__file__), 'compositing.py')

nukePath = r"C:\Program Files\Nuke8.0v5\python.exe"
if not osp.exists(nukePath):
    nukePath = r"C:\Program Files\Nuke9.0v4\python.exe"


class CompMaker(object):
    def __init__(self, parent=None):
        self.parentWin = parent
        
    def setStatus(self, status):
        if self.parentWin:
            self.parentWin.setStatus(status)
            
    def setSubStatus(self, msg):
        if self.parentWin:
            self.parentWin.setSubStatus(msg)
    
    def make(self, shots):
        os.chdir(osp.dirname(nukePath))
        command = 'python %s'%(compositingFile)
        with open(osp.join(compositingDir, 'info.txt'), 'w') as f:
            f.write(str([False, homeDir] + shots))
        self.setStatus('Creating and rendering comps')
        subprocess.call(command, shell=True)
        
    def rename(self, frames):
        renderPath = osp.join(compPath, 'renders')
        for shot, frame in frames.items():
            shotPath = osp.join(renderPath, shot)
            if not osp.exists(shotPath): continue
            files = sorted(os.listdir(shotPath))
            for ph, fr in zip(files, frame):
                name = re.sub('\.\d+\.', '.'+ str(fr) +'.', ph)
                path = osp.join(shotPath, name)
                os.rename(osp.join(shotPath, ph), path)
                iutil.addFrameNumber(path, str(fr))