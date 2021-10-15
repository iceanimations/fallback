'''
Created on Jun 17, 2016

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog, qApp
from multiShotExport.src import backend
import qtify_maya_window as qtfy
import pymel.core as pc
import os.path as osp
import appUsageApp
import subprocess
import fillinout
import imaya
import cui
import os

reload(cui)
reload(imaya)
reload(backend)

rootPath = osp.dirname(osp.dirname(__file__))
uiPath = osp.join(rootPath, 'ui')

__title__ = 'Export Snapshots'

Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
class UI(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(UI, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(__title__)
        
        self.progressBar.hide()
        
        self.cameraBox = cui.MultiSelectComboBox(self, '--Select Cameras--', triState=True)
        self.horizontalLayout.insertWidget(0, self.cameraBox)
        
        self.exportButton.clicked.connect(self.export)
        self.browseButton.clicked.connect(self.setPath)
        self.populateCameraBox()
        
        appUsageApp.updateDatabase('exportSnapshots')
        
    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=__title__, **kwargs)
    
    def closeEvent(self, event):
        self.deleteLater()
        
    def populateCameraBox(self):
        cameras = [cam.firstParent().name() for cam in imaya.getCameras(renderableOnly=False, allowOrthographic=False)]
        if cameras:
            self.cameraBox.addItems(cameras)
        else:
            self.showMessage(msg='No camera found in the scene',
                             icon=QMessageBox.Information)
            
    def getPath(self):
        path = self.pathBox.text()
        if not osp.exists(path):
            self.showMessage(msg='System could not find the path specified',
                             icon=QMessageBox.Warning)
            path = ''
        return path
    
    def setPath(self):
        filename = QFileDialog.getExistingDirectory(self, 'Select Folder', '')
        if filename:
            self.pathBox.setText(filename)
    
    def export(self):
        imgMgcPath = "C:\\Program Files\\ImageMagick-6.9.1-Q8"
        if not osp.exists(imgMgcPath):
            self.showMessage(msg='Image Magic library is not installed, could continue', icon=QMessageBox.Information)
            return
        try:
            path = self.getPath()
            if path:
                cameras = self.cameraBox.getState()
                if not cameras:
                    self.showMessage(msg='No camera selected to export the snapshot for',
                                     icon=QMessageBox.Warning)
                    return
                self.progressBar.setMaximum(len(cameras))
                self.progressBar.show()
                qApp.processEvents()
                backend.hideFaceUi()
                backend.hideShowCurves(True)
                for i, data in enumerate(cameras.items()):
                    cam, state = data
                    if state == 0: continue;
                    outPath = osp.join(path, cam).replace('\\', '/') + '.jpg'
                    if osp.exists(outPath):
                        if self.overwriteExistingButton.isChecked():
                            os.remove(outPath)
                        else:
                            self.progressBar.setValue(i+1)
                            qApp.processEvents()
                            continue
                    overscan = pc.camera(cam, overscan=True, q=True)
                    panZoomEnabled = pc.PyNode(cam).panZoomEnabled.get()
                    pc.PyNode(cam).panZoomEnabled.set(0)
                    pc.camera(cam, e=True, overscan=1)
                    pc.lookThru(cam)
                    pc.select(cam)
                    fillinout.fill()
                    snap = imaya.snapshot([1920, 1080])
                    startPath = outPath
                    name = cam
                    if state == 2:
                        startPath = osp.splitext(outPath)[0] +'_in.jpg'
                        name = cam + '_IN'
                    subprocess.call('\"'+ osp.join(imgMgcPath, 'convert.exe') +'\" %s -undercolor #00000060 -pointsize 35 -channel RGBA -fill white -draw "text 800,1050 %s" %s'%(snap, name, startPath), shell=True)
                    if state == 2:
                        pc.currentTime(pc.playbackOptions(q=True, maxTime=True))
                        snap2 = imaya.snapshot([1920, 1080])
                        endPath = osp.splitext(outPath)[0] +'_out.jpg'
                        name = cam + '_OUT'
                        subprocess.call('\"'+ osp.join(imgMgcPath, 'convert.exe') +'\" %s -undercolor #00000060 -pointsize 35 -channel RGBA -fill white -draw "text 800,1050 %s" %s'%(snap2, name, endPath), shell=True)
                    self.progressBar.setValue(i+1)
                    qApp.processEvents()
                    pc.camera(cam, e=True, overscan=overscan)
                    pc.PyNode(cam).panZoomEnabled.set(panZoomEnabled)
                if self.openFolderButton.isChecked():
                    subprocess.Popen('explorer %s'%osp.normpath(path))
        except Exception as ex:
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        finally:
            self.progressBar.hide()
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(0)
            backend.showFaceUi()
            backend.hideShowCurves(False)