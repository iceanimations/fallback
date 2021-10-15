'''
Created on Apr 4, 2015

@author: qurban.ali
'''
import pymel.core as pc
import appUsageApp
from uiContainer import uic
import qtify_maya_window as qtfy
from PyQt4.QtGui import QMessageBox, QFileDialog
import msgBox
import os.path as osp
import qutil
from loader.command.python import RedshiftAOVTools

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

__title__ = 'Add IDs'

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Window(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.addButton.clicked.connect(self.add)
        
        appUsageApp.updateDatabase('AddIDs')
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title=__title__, **kwargs)

    def add(self):
        ids = [int(self.id1.text()), int(self.id2.text()), int(self.id3.text())]
        aovName = self.nameBox.text()
        if not aovName:
            self.showMessage(msg='Name not specified for the AOV')
            return
        objs = pc.ls(sl=True)
        if len(objs) != 3:
            self.showMessage(msg='Select only 3 objects and try again')
            return
        aovs = set(pc.ls(type=pc.nt.RedshiftAOV))
        pc.mel.redshiftCreateAov("Puzzle Matte")
        aov = None
        if aovs:
            newAovs = set(pc.ls(type=pc.nt.RedshiftAOV))
            newAovs.difference_update(aovs)
            if len(newAovs) == 1:
                aov = newAovs.pop()
        else:
            aov = pc.ls(type=pc.nt.RedshiftAOV)[0]
        if aov:
            aov.redId.set(ids[0])
            aov.greenId.set(ids[1])
            aov.blueId.set(ids[2])
            aov.mode.set(1)
            aov.enabled.set(0)
            pc.editRenderLayerAdjustment(aov.enabled)
            aov.enabled.set(1)
            pc.rename(aov, aovName)
        count = 0
        for obj in objs:
            for shape in obj.getShapes():
                shape.rsObjectId.set(ids[count])
            count += 1
        RedshiftAOVTools.fixAOVPrefixes()
        self.statusBar().showMessage("IDs added successfully", 2000)
        pc.mel.redshiftUpdateActiveAovList()