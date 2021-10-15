'''
Created on Apr 6, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, QFileDialog
import os
import re
import os.path as osp
import qtify_maya_window as qtfy
import pymel.core as pc
import appUsageApp
import msgBox
import qutil

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')
__title__ = 'Add Characters'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Window(Form, Base):
    _previousPath = ''
    _playlist = None
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.errorsList = []
        
        self.progressBar.hide()
        
        self.createButton.clicked.connect(self.applyCache)
        self.browseButton.clicked.connect(self.setPath)
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=__title__, **kwargs)
        
    def getPath(self):
        path = self.pathBox.text()
        if not path or not osp.exists(path):
            self.showMessage(msg='The system could find the path specified',
                             icon=QMessageBox.Information)
            path = ''
        return path
    
    def setPath(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', '', '*.txt')
        if filename:
            self.pathBox.setText(filename)
            
    def getMapping(self):
        path = self.getPath()
        if path:
            with open(path, 'r') as f:
                return eval(f.read())
            
    def getCombinedMesh(self, ref):
        '''returns the top level meshes from a reference node'''
        meshes = []
        if ref:
            for node in pc.FileReference(ref).nodes():
                if type(node) == pc.nt.Mesh:
                    try:
                        node.firstParent().firstParent()
                    except pc.MayaNodeError:
                        if not node.isIntermediate():
                            meshes.append(node.firstParent())
                    except Exception as ex:
                        self.errorsList.append('Could not retrieve combined mesh for Reference\n'+ref.path+'\nReason: '+ str(ex))
        return meshes
    
    def getMeshFromSet(self, ref):
        meshes = []
        if ref:
            try:
                _set = [obj for obj in ref.nodes() if 'geo_set' in obj.name()
                        and type(obj)==pc.nt.ObjectSet ][0]
                meshes = [shape
                        for transform in pc.PyNode(_set).dsm.inputs(type="transform")
                        for shape in transform.getShapes(type = "mesh", ni = True)]
                #return [pc.polyUnite(ch=1, mergeUVSets=1, *_set.members())[0]] # put the first element in list and return
                combinedMesh = pc.polyUnite(ch=1, mergeUVSets=1, *meshes)[0]
                combinedMesh.rename(qutil.getNiceName(_set) + '_combinedMesh')
                return [combinedMesh] # put the first element in list and return
            except:
                return meshes
        return meshes     
        
    def addRef(self, path):
        try:
            namespace = os.path.basename(path)
            namespace = os.path.splitext(namespace)[0]
            match = re.match('(.*)([-._]v\d+)(.*)', namespace)
            if match:
                namespace = match.group(1) + match.group(3)
            return pc.createReference(path, namespace=namespace, mnc=False)
        except Exception as ex:
            self.errorsList.append('Could not create Reference for\n'+ path +'\nReason: '+ str(ex))
            
    def applyCache(self):
        '''applies cache on the combined models connected to geo_sets
        and exports the combined models'''
        mapping = self.getMapping()
        if mapping:
            self.progressBar.show()
            self.progressBar.setMaximum(len(mapping))
            count = 1
            for cache, path in mapping.items():
                cacheFile = cache+'.xml'
                if osp.exists(cacheFile):
                    if path:
                        if osp.exists(path):
                            ref = self.addRef(path)
                            meshes = self.getCombinedMesh(ref)
                            if len(meshes) != 1:
                                meshes = self.getMeshFromSet(ref)
                            if meshes:
                                if len(meshes) == 1:
                                    pc.mel.doImportCacheFile(cacheFile.replace('\\', '/'), "", meshes, list())
                                else:
                                    self.errorsList.append('Unable to identify Combined mesh or ObjectSet\n'+ path +'\n'+ '\n'.join(meshes))
                                    pc.delete(meshes)
                                    ref.remove()
                            else:
                                self.errorsList.append('Could not find or build combined mesh from\n'+path)
                                ref.remove() 
                        else:
                            self.errorsList.append('LD path does not exist for '+cache+'\n'+ path)
                    else:
                        self.errorsList.append('No LD added for '+ cache)
                else:
                    self.errorsList.append('cache file does not exist\n'+ cache)
                self.progressBar.setValue(count)
                count += 1
            self.progressBar.setValue(0)
            self.progressBar.hide()
        else:
            self.errorsList.append('No mappings found in the file')
        if self.errorsList:
            self.showErrors()
            
    def showErrors(self):
        details = '\n\n'.join(self.errorsList)
        self.showMessage(msg='Errors occurred while creating scene',
                         icon=QMessageBox.Information,
                         details=details)
        del self.errorsList[:]
            
    
    def closeEvent(self, event):
        self.deleteLater()