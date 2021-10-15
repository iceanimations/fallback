'''
Created on Jul 28, 2014

@author: Qurban Ali
'''
import os.path as osp
import os
import sys

directory = r'\\nas\storage\.db\ai_batch_render'
def check_info(__maya_version__):
    global directory
    info = {}
    if osp.exists('C:/Program Files/Autodesk/Maya'+__maya_version__+'/bin/maya.exe'):
        info['maya'] = True
    else: info['maya'] = False

    if osp.exists("C:/solidangle/mtoadeploy/"+__maya_version__+"/plug-ins/mtoa.mll"):
        info['arnold'] = True
    else: info['arnold'] = False

    f = open(osp.join(directory, os.environ.get('COMPUTERNAME')+'.txt'), 'w+')
    f.write(str(info))
    f.close()

if __name__ == "__main__":
    check_info(sys.argv[1])