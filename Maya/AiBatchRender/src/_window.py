'''
Created on Aug 4, 2014

@author: Qurban Ali
'''
import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import QFileDialog, qApp
import os
import pymel.core as pc
import qtify_maya_window as qtfy
import os.path as osp
import re
import maya.cmds as cmds
import multiprocessing as mp
from multiprocessing.pool import ThreadPool
import subprocess

directory = r'\\nas\storage\.db\ai_batch_render'
__maya_version__ = re.search('\\d{4}', pc.about(v=True)).group()
user = osp.expanduser('~')
rootPath = osp.dirname(osp.dirname(__file__))

def submit_job(command):
    subprocess.call(command, shell=True)

Form, Base = uic.loadUiType("%s/ui/main.ui"%rootPath)
class Window(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.renderButton.clicked.connect(self.render)
        self.usernameBox.setText(os.environ.get("USERNAME"))
        self.passwordBox.setFocus()
        self.browseButton.clicked.connect(self.browse)
        
    def closeEvent(self, event):
        self.deleteLater()
    
    def hideEvent(self, event):
        self.close()
        
    def browse(self):
        filename = QFileDialog.getExistingDirectory(self, "Project Folder", '')
        if filename:
            self.projectBox.setText(filename)
        
    def render(self):

        username = str(self.usernameBox.text())
        password = str(self.passwordBox.text())
        project = str(self.projectBox.text())
        if not osp.exists(project):
            pc.warning("project path does not exist")
            return
        if not username:
            pc.warning("username not specified")
            return
        if not password:
            pc.warning("password not specified")
            return
        self.statusLabel.setText('Checking remote systems...')
        qApp.processEvents()
        nodes = self.find_live_nodes(username, password)
        if not nodes:
            pc.warning("No machine ready to render")
            return
        else:
            self.statusLabel.setText(str(len(nodes))+' systems ready')
            qApp.processEvents()
            
        self.ai_render(username, password, project, nodes)
        
    def get_info(self, systm):
        try:
            global directory
            f = open(directory + systm+'.txt')
            result = eval(f.read())
            f.close()
            if (result['maya'] and result['arnold']):
                return True
            return False
        except IOError as e:
            if '050' in systm:
                print e
            return False
        
    def find_live_nodes(self, uname, pswd):
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
        #f = open(tempFile, 'w+')
        #f.write('call \\\\nas\\storage\\scripts\\mount.bat\n'+
                #'R:\\Pipe_Repo\\Users\\Qurban\\applications\\Python26\\python.exe R:\\Pipe_Repo\\Users\\Qurban\\utilities\\sysinfo.py '+__maya_version__)
        #f.close()
        #for systm in systems:
            #subprocess.call('psexec \\'+systm+' -u ICEANIMATIONS\\'+uname+' -p '+pswd+' -c -f '+tempFile, shell=True)
        for syst in systems:
            if self.get_info(syst):
                good_systems.append(syst)
        print good_systems
        return good_systems
    
    def ai_render(self, uname, pswd, project_path, nodes, file_path=cmds.file(location=True, q=True)):
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
        for _ in nodes:
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
        psexecCommands = []
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
            psexecCommands.append("psexec \\"+ nodes[nodeCount] +" -u ICEANIMATIONS\\"+uname+" -p "+pswd+" -c -f "+ fullFileName)
            nodeCount += 1
        pool = ThreadPool(processes=len(psexecCommands))
        itr = pool.imap_unordered(submit_job, psexecCommands)
        done = []
        self.statusLabel.setText('0 of '+str(len(psexecCommands))+' done')
        while 1:
            try:
                done.append(itr.next(timeout=0.01))
                self.statusLabel.setText(str(len(done))+' of '+str(len(psexecCommands))+' done')
            except mp.TimeoutError:
                pass
            except StopIteration:
                break
            qApp.processEvents()
        self.statusLabel.setText('')
