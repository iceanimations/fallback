'''
Created on Jul 6, 2015

@author: qurban.ali
'''
import pymel.core as pc
import jobs

def addScriptJobs():
    for job in pc.scriptJob(lj=True):
        if 'SceneOpened' in job:
            if 'showFPSDialog' in job:
                return
    pc.scriptJob(event=['SceneOpened', jobs.showFPSDialog])