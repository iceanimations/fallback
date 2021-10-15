'''
Created on Oct 26, 2013

@author: qurban.ali

this script saves the current file as new file in the same directory
and appends number (001, 002, 003...) to the end of file name
'''
import os
import os.path as osp
import maya.cmds as cmds
import re

# update the database, how many times this app is used
import site
site.addsitedir(r'r:/pipe_repo/users/qurban')
import appUsageApp
appUsageApp.updateDatabase('Save_Increment')

def saveFile():
    fileName = cmds.file(q = True, location = True)
    if fileName == "unknown" or not fileName:
        cmds.warning("Save the file first, then try to save as increments")
        return
    dirname, basename = osp.split(fileName)
    basename, ext = osp.splitext(basename)
    
    newName = incFileName(basename)
    newName = newName
    
    if ext == ".mb": typ = "mayaBinary"
    else: typ = "mayaAscii"
    
    cmds.file(rename = osp.join(dirname, newName))
    cmds.file(f = True, save = True,  options = "v=0;", type = typ)

def incFileName(name):
    names = name.split("_")
    if len(names) > 1:
        num = names[-1]
        length = len(num)
        num = str(int(num) + 1)
        newName = ''
        for i in range(len(names) - 1):
            newName += names[i] +'_'
    else:
        m = re.search("(\d+)", name)
        if m:
            num = m.group(0)
            length = len(num)
            newName = name.replace(str(num), '')
        else: num = "000"
        num = str(int(num) + 1)
    return newName + num.zfill(length)