'''
Created on Jul 28, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog, QPushButton, qApp, QRadioButton
import os.path as osp
import qtify_maya_window as qtfy
import msgBox
import qutil
reload(qutil)
import os
import re
import cui
reload(cui)
import appUsageApp
reload(appUsageApp)
import backend.renderer as renderer
reload(renderer)
import shutil
import pymel.core as pc
from collections import OrderedDict

rootPath = qutil.dirname(__file__, depth=2)
uiPath = osp.join(rootPath, 'ui')

# to import the rendering_helper.py
os.environ['PYTHONPATH'] += os.pathsep + osp.join(rootPath, 'src', 'backend')

title = 'Render Shots'
homeDir = renderer.homeDir
# keys for option vars
resolution_key = 'renderShots_resolution'
shotsPath_key = 'renderShots_shotsPath'

Form, Base = uic.loadUiType(osp.join(uiPath, 'main.ui'))
class RenderShotsUI(Form, Base):
    '''
    Takes input from the user for scene rendering
    '''
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(RenderShotsUI, self).__init__(parent)
        self.setupUi(self)
        
        self.setWindowTitle(title)
        self.shotsBox = cui.MultiSelectComboBox(self, '--Select Shots--')
        self.pathLayout.addWidget(self.shotsBox)
        self.lastPath = ''
        
        self.resolutions = OrderedDict()
        self.resolutions['320x240'] = [320, 240, 1.333]
        self.resolutions['640x480'] = [640, 480, 1.333]
        self.resolutions['960x540'] = [960, 540, 1.777]
        self.resolutions['1280x720'] = [1280, 720, 1.777]
        self.resolutions['1920x1080'] = [1920, 1080, 1.777]
        
        
        self.renderButton.clicked.connect(self.render)
        self.browseButton.clicked.connect(self.setPath)
        self.shotsPathBox.textChanged.connect(self.populateShots)
        self.resolutionBox.activated.connect(self.resolutionBoxActivated)
        
        self.setupWindow()
        
        appUsageApp.updateDatabase('renderShots')
        
    def resolutionBoxActivated(self):
        qutil.addOptionVar(resolution_key, self.resolutionBox.currentText())
        
    def setupWindow(self):
        # setup the resolution box
        self.resolutionBox.addItems(self.resolutions.keys())
        val = qutil.getOptionVar(resolution_key)
        if val:
            for i in range(self.resolutionBox.count()):
                text = self.resolutionBox.itemText(i)
                if text == val:
                    self.resolutionBox.setCurrentIndex(i)
                    break
        # set shots path
        val = qutil.getOptionVar(shotsPath_key)
        if val:
            self.shotsPathBox.setText(val)
            self.lastPath = val
        
    def getResolution(self):
        return self.resolutions[self.resolutionBox.currentText()]
        
    def render(self):
        try:
            for directory in os.listdir(homeDir):
                name = osp.join(homeDir, directory)
                if osp.isdir(name):
                    shutil.rmtree(name)
        except Exception as ex:
            self.showMessage(msg=str(ex),
                             icon=QMessageBox.Information)
            return

        import backend.collageMaker as collageMaker
        reload(collageMaker)
        import backend.compMaker as compMaker
        reload(compMaker)
        if not osp.exists(compMaker.nukePath):
            self.showMessage(msg='It seams like Nuke8.0v5 or Nuke9.0v4 is not installed, please install one',
                             icon=QMessageBox.Information)
            return

        errors = {}
        renderableFiles = {}
        shots = self.shotsBox.getSelectedItems()
        if not shots:
            shots = self.shotsBox.getItems()
        for shot in shots:
            filesDirectory = osp.join(self.getShotsPath(), shot, 'lighting', 'files')
            if not osp.exists(filesDirectory):
                errors[filesDirectory] = 'Directory does not exist'
                continue
            files = [phile for phile in os.listdir(filesDirectory) if osp.isfile(osp.join(filesDirectory, phile)) and osp.splitext(phile)[-1] in ['.ma', '.mb']]
            if not files:
                errors[filesDirectory] = 'No maya file found'
                continue
            if len(files) > 1:
                sb = cui.SelectionBox(self, [QRadioButton(name, self) for name in files], 'More than one files found in %s, please select one'%filesDirectory)
                sb.setCancelToolTip('Press to skip this shot')
                if not sb.exec_():
                    continue
                files = sb.getSelectedItems()
            renderableFiles[shot] = osp.join(filesDirectory, files[0])
        if errors:
            btn = self.showMessage(msg='Problems have been detected in the specified directory',
                                   ques='Do you want to continue?',
                                   icon=QMessageBox.Question,
                                   btns=QMessageBox.Yes|QMessageBox.No,
                                   details=qutil.dictionaryToDetails(errors))
            if btn == QMessageBox.No:
                return
        # render the shots
        rdr = renderer.Renderer(self)
        length = len(renderableFiles)
        i = 1
        ws = pc.workspace(q=True, o=True)
        pc.workspace(homeDir, o=True)
        frames = {}
        for shot, filename in renderableFiles.items():
            f = open(osp.join(homeDir, 'info.txt'), 'w')
            f.write(shot)
            f.close()
            self.setStatus('<b>Rendering %s (%s of %s)</b>'%(shot, i, length))
            frame = rdr.render(filename)
            if not frame:
                with open(osp.join(homeDir, 'info1.txt')) as f:
                    frame = eval(f.read())
            frames[shot] = frame
            i += 1
        
        # create comps for each shot
        cm = compMaker.CompMaker(self)
        cm.make(renderableFiles.keys())
        cm.rename(frames)
        
        #create collage for each shot
        cm = collageMaker.CollageMaker(self)
        for shot in renderableFiles.keys():
            cm.makeShot(shot)
        path = cm.make()
        self.showMessage(msg='<a href=\"%s\" style=\"color: lightGreen\"'%path.replace('\\', '/') + '>' + path + '</a>')

        pc.workspace(ws, o=True)
        self.setStatus('')
        self.setSubStatus('')
    
    def setStatus(self, msg):
        self.statusLabel.setText(msg)
        qApp.processEvents()
        
    def setSubStatus(self, msg):
        self.subStatusLabel.setText(msg)
        qApp.processEvents()
    
    def setPath(self):
        filename = QFileDialog.getExistingDirectory(self, title, self.lastPath, QFileDialog.ShowDirsOnly)
        if filename:
            self.lastPath = filename
            self.shotsPathBox.setText(filename)
            
    def showMessage(self, **kwargs):
        return cui.showMessage(self, title=title, **kwargs)
            
    def getShotsPath(self, msg=True):
        path = self.shotsPathBox.text()
        if (not path or not osp.exists(path)) and msg:
            self.showMessage(msg='The system could not find the path specified',
                             icon=QMessageBox.Information)
            path = ''
        return path
    
    def populateShots(self):
        path = self.getShotsPath(msg=False)
        if path:
            shots = [shot for shot in os.listdir(path) if re.match('SQ\\d{3}_SH\\d{3}', shot)]
            self.shotsBox.addItems(shots)
            qutil.addOptionVar(shotsPath_key, path)
    
    def closeEvent(self, event):
        self.deleteLater()
        event.accept()