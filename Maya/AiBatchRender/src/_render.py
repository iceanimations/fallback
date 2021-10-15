'''
Created on Jul 17, 2014

@author: qurban.ali
'''

import os.path as osp
import os
import subprocess
import re
import _sysinfo as si
reload(si)
import maya.cmds as cmds
import pymel.core as pc
user = osp.expanduser('~')
__maya_version__ = re.search('\\d{4}', pc.about(v=True)).group()

def find_live_nodes(uname, pswd):
    '''returns the list of all connected computers in a LAN'''
    os.system('net view > conn.tmp')
    f = open('conn.tmp', 'r')
    f.readline();f.readline();f.readline()
    
    tempFile = osp.join(user, 'tempfile.bat')
    
    conn = []
    host = f.readline()
    while host[0] == '\\':
        conn.append(host[:host.find(' ')])
        host = f.readline()
    f.close()
    #conn = ['\\ICE-088', '\\ICE-089', '\\ICE-185', '\\ICE-099', '\\ICE-131']
    systems = []
    good_systems = []
    for con in conn:
        result = re.match('\\\\\\\\ICE-\\d{3}', con)
        if result:
            systems.append(con)
    print systems
    f = open(tempFile, 'w+')
    f.write('call \\\\nas\\storage\\scripts\\mount.bat\n'+
            'R:\\Pipe_Repo\\Users\\Qurban\\applications\\Python26\\python.exe R:\\Pipe_Repo\\Users\\Qurban\\utilities\\sysinfo.py '+__maya_version__)
    f.close()
    for systm in systems:
        os.system('psexec \\'+systm+' -u ICEANIMATIONS\\'+uname+' -p '+pswd+' -c -f '+tempFile)
    for syst in systems:
        if si.get_info(syst):
            good_systems.append(syst)
    return good_systems

def ai_render(uname, pswd, project_path, nodes, file_path=cmds.file(location=True, q=True)):
    '''renders the scene in chuncks by sending each chunck
    to a sepearate computer using psexec.exe'''

    if file_path == 'unknown':
        pc.warning("Save the file first")
        return
    res = pc.ls(type='resolution')[0]
    width = res.width.get()
    height = res.height.get()

    numNodes = len(nodes)
    quotient = height/numNodes
    remender = height%numNodes
    
    lastPixel = -1
    yEnd = quotient - 1
    count = 1
    commands = []
    for node in nodes:
        name = osp.splitext(osp.basename(file_path))[0] +"_"+ str(count).zfill(3)
        command = "render.exe -proj "+project_path+" -r arnold -im "+ name+ " -reg %s %s %s %s %s"%(0, width-1, lastPixel+1, yEnd, file_path)
        commands.append(command)
        lastPixel = yEnd
        yEnd += quotient
        if yEnd > height:
            if remender > 0:
                count += 1
                name = osp.splitext(osp.basename(file_path))[0] +"_"+ str(count)
                command = "render.exe -proj "+project_path+" -r arnold -im "+ name+ " -reg %s %s %s %s %s"%(0, width-1, lastPixel+1, lastPixel+remender, file_path)
                commands.append(command)
        count += 1
    nodeCount = 0
    if len(commands) > len(nodes):
        nodes.append(nodes[-1])
    for cmd in commands:
        fileName = 'ai_render_'+ str(nodeCount) + '.bat'
        fullFileName = osp.join(user, fileName)
        f = open(fullFileName, 'w+')
        f.write("call \\\\nas\\storage\\scripts\\mount.bat"+
                "\nset MAYA_RENDER_DESC_PATH=C:\\solidangle\\mtoadeploy\\"+__maya_version__+
                "\nset PATH=C:\\solidangle\\mtoadeploy\\"+__maya_version__+"\\bin;%path%"+
                "\nset MAYA_MODULE_PATH=C:\\solidangle\\mtoadeploy\\"+__maya_version__+
                "\nset MAYA_PLUG_IN_PATH=C:\\solidangle\\mtoadeploy\\"+__maya_version__+"\\plug-ins"+
                "\nset PATH=C:\\Program Files\\Autodesk\Maya"+__maya_version__+"\\bin;%path%\n" + cmd)
        f.close()
        psexec = "psexec -d \\"+ nodes[nodeCount] +" -u ICEANIMATIONS\\"+uname+" -p "+pswd+" -c -f "+ fullFileName
        os.system(psexec)
        nodeCount += 1
