import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import shaderTransferCombo
import qtify_maya_window as utl
import utilities as util
import os.path as osp
import stCtoC
import stStoS
map(lambda x: reload(x), [stStoS, stCtoC, util])

def createUI():
    Form, Base = uic.loadUiType(r'%s\\ui\\uiCombo.ui' % osp.dirname(shaderTransferCombo.__file__))
    class Category(Form, Base):
        def __init__(self, parent = utl.getMayaWindow()):
            super(Category, self).__init__(parent)
            self.setupUi(self)
            self.transferButton.clicked.connect(self.transfer)
            self.transferPolicyBox.currentIndexChanged.connect(self.handleComboBox)
            self.addSourceButton.clicked.connect(self.addSourceObjects)
            self.addTargetButton.clicked.connect(self.addTargetObjects)
            self.removeAllButton.clicked.connect(self.removeAll)
            self.removeSelectionButton.clicked.connect(self.removeSelection)
            self.closeButton.clicked.connect(self.closeWindow)
            self.uvButton.clicked.connect(self.switchUVButton)
            self.move(getParentWindowPos(parent, self))
            self.sBar = self.statusBar()
            self.handleComboBox()
            self.sourceObject = None
            self.targetObjects = []
            self.transferUVs = False
            #msgBox(self, msg = 'Before transfering the shaders, please make sure that'+
            #' all source and target objects are IMPORTED, neither REFERENCED nor directly OPENED.'+
            #' Other wise the shaders may not be transfered or may not be properly transfered')
            #update the database
            import site
            site.addsitedir(r'R:/pipe_Repo/users/Qurban')
            import appUsageApp
            appUsageApp.updateDatabase('shaderTransfer')
            
        def switchUVButton(self):
            '''
            sets the "transferUVs" variable to True or False
            '''
            self.transferUVs = self.uvButton.isChecked()
            
        def closeWindow(self):
            '''closes the main window and deletes it'''
            self.close()
            self.deleteLater()
        
        def setStatus(self, msg):
            '''sets the message for the status bar of main window'''
            self.sBar.showMessage(msg, 3000)
            
        def addSourceObjects(self):
            '''adds source objects to the list'''
            if not util.isSelected():
                msgBox(self, msg = 'The system can not find any selection in the current scene',
                       icon = QMessageBox.Warning)
                return
            objs = util.selectedObjects(self.transferPolicy)
            if objs:
                self.sourceBox.setText(objs[0])
                self.sourceObject = objs[0]
            else: msgBox(self, msg = 'Selected object does not match the selected policy',
                         icon = QMessageBox.Warning)

        def addTargetObjects(self):
            '''adds the target objects to list'''
            if not util.isSelected():
                msgBox(self, msg = 'The system can not find any selection in the current scene',
                       icon = QMessageBox.Warning)
                return
            objects = util.selectedObjects(self.transferPolicy)
            if objects:
                for obj in objects:
                    item = QListWidgetItem()
                    item.setText(obj)
                    self.targetBox.addItem(item)
                    self.targetObjects.append(obj)
            else:
                msgBox(self, msg = 'Selected object(s) type does not match the selected policy',
                       icon = QMessageBox.Warning)
        
        def removeAll(self):
            '''removes all the added objects from both lists'''
            self.targetBox.clear()
            self.targetObjects = []
            
        def removeSelection(self):
            '''removes the selected objects from the both lists'''
            for selectedItem in self.targetBox.selectedItems():
                self.targetObjects.remove(str(self.targetBox.takeItem(self.targetBox.indexFromItem(selectedItem).row()).text()))

        def handleComboBox(self):
            '''handles when the current index of the comboBox is changed'''
            text = str(self.transferPolicyBox.currentText())
            self.removeAll()
            self.sourceBox.clear()
            self.sourceObject = None
            if text == 'Combined to Combined':
                self.setStatus('Selection type should be Mesh')
                self.addSourceButton.setText('Add Source Mesh')
                self.addTargetButton.setText('Add Target Mesh')
                self.transferPolicy = 'ctoc'
            if text == 'Separate to Separate':
                self.setStatus('Selection type should be Set')
                self.addSourceButton.setText('Add Source Set')
                self.addTargetButton.setText('Add Target Set')
                self.transferPolicy = 'stos'


            """if text == 'Combined to Separate':
                self.setStatus('')
            if text == 'Separate to Combined':
                self.setStatus('')"""
        def transfer(self):
            '''calls the appropraite function to transfer the shaders'''
            if not self.sourceBox.text():
                msgBox(self, msg = 'Source object is not added to the field',
                       icon = QMessageBox.Warning)
                return
            if not self.targetBox.count():
                msgBox(self, msg = 'Target objects are not added to list',
                       icon = QMessageBox.Warning)
                return
            badFaces = {} # number of faces is different in source and target meshes
            badLength = [] # number of meshes is different in source and target sets
            loadBox = load()
            if self.transferPolicy == 'ctoc':
                badFaces.update(stCtoC.main(self.sourceObject, self.targetObjects, self.transferUVs))
            if self.transferPolicy == 'stos':
                faces, length = stStoS.main(self.sourceObject, self.targetObjects, self.transferUVs)
                badFaces.update(faces)
                badLength += length
                
            """if text == 'Combined to seperate':
                stCtoS.createClass()
            if text == 'Seperate to combined':
                stStoC.createClass()"""
            loadBox.deleteLater()
            if badFaces:
                keys = badFaces.keys()
                nKeys = len(keys)
                detail = 'Face count does not match for the following Meshes:\n'
                for i in range(nKeys):
                    detail += str(i+1) + ': '+ keys[i] +' and '+ badFaces[keys[i]] +'\n'
                msgBox(self, msg = 'Number of faces does not match for the Meshes',
                       details = detail, icon = QMessageBox.Warning)
            if badLength:
                detail = 'Following source meshes not found in target set:\n'
                for i in range(len(badLength)):
                    detail += str(i+1) + ': '+ badLength[i] +'\n'
                msgBox(self, msg = 'Number of meshes in Target sets do not match the number of meshes in the Source Set',
                       icon = QMessageBox.Warning, details = detail)
    
    global shTransfer
    shTransfer = Category()
    shTransfer.show()
    
def load():
    Form, Base = uic.loadUiType(r'%s\\ui\\load.ui' % osp.dirname(shaderTransferCombo.__file__))
    class Load(Form, Base):
        def __init__(self, parent = utl.getMayaWindow()):
            super(Load, self).__init__(parent)
            self.setupUi(self)
            self.setWindowModality(Qt.ApplicationModal)
            self.move(getParentWindowPos(parent, self))
            s = self.size()
            self.setFixedSize(s)
            
    global loadingBox
    loadingBox = Load()
    loadingBox.show()
    loadingBox.repaint(1, 1, 1, 1)
    return loadingBox

def msgBox(parent, msg = None, btns = QMessageBox.Ok,
           icon = None, ques = None, details = None):
    '''
    dispalys the warnings
    @params:
            args: a dictionary containing the following sequence of variables
            {'msg': 'msg to be displayed'[, 'ques': 'question to be asked'],
            'btns': QMessageBox.btn1 | QMessageBox.btn2 | ....}
    '''
    if msg:
        mBox = QMessageBox()
        mBox.setWindowModality(Qt.ApplicationModal)
        mBox.setWindowTitle('Shader Transfer')
        mBox.setText(msg)
        if ques:
            mBox.setInformativeText(ques)
        if icon:
            mBox.setIcon(icon)
        if details:
            mBox.setDetailedText(details)
        mBox.setStandardButtons(btns)
        buttonPressed = mBox.exec_()
        return buttonPressed
    
def getParentWindowPos(parent, child):
    '''
    returns the mid point of the "parent window for "child"
    ''' 
    parentCenter = QPoint(parent.width() / 2, parent.height() / 2)
    childCenter = QPoint(child.width() / 2, child.height() / 2)
    return   parentCenter - childCenter