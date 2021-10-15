'''
Created on Jun 17, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QMessageBox, qApp
import os
import os.path as osp
import qtify_maya_window as qtfy
import pymel.core as pc
import appUsageApp
reload(appUsageApp)
import msgBox


root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

def getSGNode(mtl):
    try:
        outputs = mtl.outColor.outputs()
        if not outputs:
            return
        if len(outputs) > 1:
            outputs = [x for x in outputs if type(x) == pc.nt.RedshiftMaterialBlender]
            if outputs:
                sg = outputs[0].outColor.outputs()[0]
        elif len(outputs) == 1:
            sg = outputs[0]
    except:
        return
    if type(sg) == pc.nt.ShadingEngine:
        return sg

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Adder(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Adder, self).__init__(parent)
        self.setupUi(self)
        
        self.refreshButton.clicked.connect(self.refresh)
        self.addButton.clicked.connect(self.AddIds)
        
        self.items = []
        self.addItems()
        
        appUsageApp.updateDatabase('AddMaterialIds')
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title='Add Material IDs', **kwargs)
        
    def getAllMaterials(self):
        try:
            old_mtls = pc.ls(type=[pc.nt.RedshiftArchitectural,
                pc.nt.RedshiftSubSurfaceScatter], sl=True)
            new_mtls = pc.ls(type='RedshiftMaterial', sl=True)
            return old_mtls + new_mtls
        except AttributeError:
            self.showMessage(msg="It seems like Redshift is not loaded or installed",
                             icon=QMessageBox.Information)
        
    def addItems(self):
        materials = self.getAllMaterials()
        if not materials:
            self.showMessage(msg='No Redshift material found in the selection',
                             icon=QMessageBox.Information)
            return
        for mtl in materials:
            sg = getSGNode(mtl)
            if sg:
                print sg
                item = Item(name=mtl.name(), ID=sg.rsMaterialId.get(), parent=self)
                self.items.append(item)
                self.itemsLayout.addWidget(item)
                
    def AddIds(self):
        for item in self.items:
            item.addId()
        if self.items:
            pc.inViewMessage(msg="IDs added to %s materials"%len(self.items), f=True, position='midCenter')
    
    def clearWindow(self):
        for item in self.items:
            item.close()
        del self.items[:]
    
    def closeEvent(self, event):
        self.deleteLater()
    
    def refresh(self):
        self.clearWindow()
        self.addItems()
        
        
Form1, Base1 = uic.loadUiType(osp.join(ui_path, 'item.ui'))
class Item(Form1, Base1):
    def __init__(self, name='', ID=None, parent=None):
        super(Item, self).__init__(parent)
        self.setupUi(self)
        
        print ID
        
        self.material = None
        if name:
            self.setName(name)
        if ID:
            self.setId(ID)
            
        self.selectButton.clicked.connect(self.selectObjects)
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def setName(self, name):
        self.nameLabel.setText(name)
    
    def setId(self, ID):
        self.idBox.setValue(int(ID))
    
    def selectObjects(self):
        mtl = pc.PyNode(self.nameLabel.text())
        sg = getSGNode(mtl)
        if sg:
            pc.select(sg.dagSetMembers.inputs())
    
    def addId(self):
        mtl = pc.PyNode(self.nameLabel.text())
        sg = getSGNode(mtl)
        if sg:
            try:
                sg.rsMaterialId.set(self.idBox.value())
            except:
                pass
