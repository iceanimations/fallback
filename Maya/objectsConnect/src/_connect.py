'''
Created on Jan 7, 2015

@author: qurban.ali
'''
import pymel.core as pc
import appUsageApp
import qtify_maya_window as qtfy
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog
import msgBox
import os.path as osp
import qutil
import maya.cmds as cmds
import subprocess
import os

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

__title__ = 'Add LD'
__log_file_path__ = osp.join(osp.dirname(osp.expanduser('~')), 'add_ld_log.txt')
__backup_directory_name__ = 'add_LD_backup'

if not osp.exists(__log_file_path__):
    with open(__log_file_path__, 'w') as f:
        pass

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class LD(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(LD, self).__init__(parent)
        self.setupUi(self)
        
        self.addButton.clicked.connect(self.CallAdd)
        self.browseButton.clicked.connect(self.setPath)
        
        self.logFile = None
        
        self.updateButton.hide()
        self.l1.hide()
        self.l2.hide()
        self.rigColumnBox.hide()
        self.ldColumnBox.hide()
        self.batchButton.toggled.connect(self.handleBatchButton)
        appUsageApp.updateDatabase('AddLD')
        
    def getRigColum(self):
        return self.rigColumnBox.value()
    
    def getLDColum(self):
        return self.ldColumnBox.value()
        
    def handleBatchButton(self, val):
        if val: self.label.setText('CSV Path:')
        else: self.label.setText('LD path:')
        
    def setPath(self):
        fileFilter = '*.csv' if self.batchButton.isChecked() else '*.ma *.mb'
        filename = QFileDialog.getOpenFileName(self, 'Select File',
                                               '', fileFilter)
        if filename:
            self.pathBox.setText(filename)
        
    def setStatus(self, msg):
        self.statusBar().showMessage(msg, 2000)
        
    def CallAdd(self):
        if self.batchButton.isChecked():
            self.addBatch()
        else:
            self.add()
            
    def createBackup(self, path):
        directory = osp.dirname(path)
        directory = osp.join(directory, __backup_directory_name__)
        if not osp.exists(directory):
            os.mkdir(directory)
        cmds.file(osp.join(directory, osp.basename(path)), ea=True, f=True, type=cmds.file(q=True, type=True)[0])
        
    def isBackup(self, path):
        directory = osp.dirname(path)
        directory = osp.join(directory, __backup_directory_name__)
        if osp.exists(directory):
            return True
        return False
        
    def addBatch(self):
        self.logFile = open(__log_file_path__, 'w')
        try:
            csvFile = self.getPath()
            if not csvFile:
                return
            data = qutil.getCSVFileData(csvFile)
            count = 1
            with open(__log_file_path__, 'w') as f:
                pass
            for item in data:
                try:
                    rig, ld = item[self.getRigColum() - 1], item[self.getLDColum() - 1]
                except IndexError:
                    self.showMessage(msg='CSV file does not contain specified columns',
                                     icon=QMessageBox.Information)
                    return
                if rig:
                    if osp.exists(rig):
                        if not self.updateButton.isChecked():
                            if self.isBackup(rig):
                                continue
                        if ld:
                            if osp.exists(ld):
                                cmds.file(rig, o=True, f=True, prompt=False)
                                self.createBackup(rig)
                                flag = False
                                for node in pc.ls(et=pc.nt.ObjectSet):
                                    if 'geo_set' in node.name().lower():
                                        print '---> Adding: '+ rig +' >> '+ ld
                                        if not pc.hasAttr(node, 'forCache'):
                                            pc.addAttr(node, shortName='forCache', longName='forCache', niceName='LD', dt='string')
                                        node.forCache.set(ld)
                                        #cmds.file(rename='D:/shot_test/file'+str(count)+osp.splitext(cmds.file(q=True, type=True)[0])[-1])
                                        cmds.file(save=True, f=True, type=qutil.getFileType())
                                        count += 1
                                        flag = True
                                        break
                                if not flag:
                                    details = ('Could not find object set or the object set is not properly named in the following file:\n'+
                                              rig+'\n')
                                    self.createLog(details)
                            else:
                                details = 'The system could not find the LD path specified for rig:\n'+rig
                                self.createLog(details)
                        else:
                            pass
                    else:
                        details = 'The system could not find the path specified for the rig:\n'+rig
                        self.createLog(details)
                else:
                    pass
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Information)
        finally: self.logFile.close(); self.logFile = None
        cmds.file(new=True, f=True)
        self.showLog()
                            
    def createLog(self, details=''):
        details = details.replace('\n', '\r\n')
        if self.logFile:
            self.logFile.write(details)
            self.logFile.write('\n\r'*3)
    
    def showLog(self):
        with open(__log_file_path__, 'r') as f:
            if f.read():
                btn = self.showMessage(msg='Errors occurred while adding LDs\nLog: '+
                                       __log_file_path__.replace('/', '\\'), icon=QMessageBox.Information,
                                       ques='Do you want to view log file now?',
                                       btns=QMessageBox.Yes|QMessageBox.No)
                if btn == QMessageBox.Yes:
                    subprocess.call('explorer '+__log_file_path__.replace('/', '\\'), shell=True)

    def add(self):
        
        objects = pc.ls(sl=True)
        if not objects:
            self.setStatus('No selection found in the scene')
            return
        
        if len(objects) > 1:
            self.setStatus('Select 1 object only (Maya object set)')
            return
        
        _set = objects[0]
        
        if not pc.hasAttr(_set, 'forCache'):
            pc.addAttr(_set, shortName='forCache', longName='forCache', niceName='LD', dt='string')
            
        # set the attribute
        path = self.getPath()
        if not path:
            return
        try:
            _set.forCache.set(path)
        except Exception as ex:
            msgBox.showMessage(self, title='Error', msg=str(ex),
                               icon=QMessageBox.Information)
            return
        
        pc.inViewMessage(amg='<hl>LD added successfully</hl>', pos='midCenter', fade=True )
    
    def getPath(self):
        path = self.pathBox.text()
        if not path:
            self.setStatus('Path not specified')
            return ''
        if not osp.exists(path):
            self.setStatus('Path does not exist')
            return ''
        if not osp.isfile(path):
            self.setStatus('Specified path is not a file')
            return ''
        if self.batchButton.isChecked():
            if osp.splitext(path)[-1] not in ['.csv']:
                self.setStatus('Specified file is not a CSV file')
                return ''
        else:
            if osp.splitext(path)[-1] not in ['.ma', '.mb']:
                self.setStatus('Specified file is not a Maya file')
                return ''
        
        return path
    
    def closeEvent(self, event):
        self.deleteLater()
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=__title__, **kwargs)