'''
Created on Feb 25, 2015

@author: qurban.ali
'''
from uiContainer import uic
from PyQt4.QtGui import QMessageBox
import os.path as osp
import qtify_maya_window as qtfy
import pymel.core as pc
import appUsageApp
import msgBox

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Window(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        if not self.copyLayer():
            self.close()
            self.deleteLater()
            return
        
        self.addButton.clicked.connect(self.addCharsProps)
        self.removeButton.clicked.connect(self.removeCharsProps)
        self.addButton2.clicked.connect(self.addOcc)
        self.removeButton2.clicked.connect(self.removeOcc)
        self.addButton3.clicked.connect(self.addMatte)
        self.removeButton3.clicked.connect(self.removeMatte)
        self.setupButton.clicked.connect(self.setup)
        
        appUsageApp.updateDatabase('setupContactLayer')
        
    def showMessage(self, **kwargs):
        return msgBox.showMessage(self, title='Setup Contact Layer', **kwargs)
        
    def copyLayer(self):
        currentLayer = pc.editRenderLayerGlobals(q=True, crl=True)
        if not currentLayer.lower().startswith('char'):
            self.showMessage(msg='Select Character layer and try again',
                             icon=QMessageBox.Information)
            return
        
        # copy the current layer
        contact = pc.duplicate(currentLayer, inputConnections=1, name='Contact')[0]
        pc.editRenderLayerGlobals(crl=contact)
        
        
        return True
    
    def addCharsProps(self):
        
        charsProps = pc.ls(sl=True, type='mesh', dag=True, ni=True)
        
        self.charsPropsBox.addItems([item.name() for item in charsProps])
        
        # turn off the primary visibility
        badObjects = []
        for obj in charsProps:
            try:
                obj.primaryVisibility.set(0)
            except:
                badObjects.append(obj)
        if badObjects:
            self.showMessage(msg='Could not turn off the primary visibility for some objects',
                             details='\n'.join(badObjects), icon=QMessageBox.Information)
            del badObjects[:]
        
    def removeCharsProps(self):
        for item in self.charsPropsBox.selectedItems():
            self.charsPropsBox.takeItem(self.charsPropsBox.row(item))
            
    def addOcc(self):
        
        occs = pc.ls(sl=True, type='mesh', dag=True, ni=True)
        self.occBox.addItems([item.name() for item in occs])
        
        # turn off the castsShadows
        badObjects = []
        for obj in occs:
            try:
                obj.castsShadows.set(0)
            except:
                badObjects.append(obj)
        if badObjects:
            self.showMessage(msg='Could not turn off the castsShadows for some objects',
                             details='\n'.join(badObjects), icon=QMessageBox.Information)
            del badObjects[:]
        
    def removeOcc(self):
        for item in self.occBox.selectedItems():
            self.occBox.takeItem(self.occBox.row(item))
            
    def addMatte(self):
        
        mattes = pc.ls(sl=True, type=pc.nodetypes.RedshiftMatteParameters)
        self.matteBox.addItems([item.name() for item in mattes])
        
        # turn on the required attrs
        badObjects = []
        for obj in mattes:
            try:
                obj.matteEnable.set(1)
                obj.matteShadowEnable.set(1)
                obj.matteAlpha.set(1)
                obj.matteShadowAffectsAlpha.set(1)
            except:
                badObjects.append(obj)
        if badObjects:
            self.showMessage(msg='Could not turn off the primary visibility for some objects',
                             details='\n'.join(badObjects), icon=QMessageBox.Information)
            del badObjects[:]
        
    def setup(self):
        # Hide all the lights
        lights = pc.ls(type=[pc.nt.RedshiftDomeLight, pc.nt.RedshiftPortalLight, pc.nt.RedshiftPhysicalLight, pc.nt.RedshiftIESLight, pc.nt.RedshiftPhysicalSun])
        lights = [light.firstParent() for light in lights]
        sl = pc.ls(sl=True)
        pc.select(lights)
        pc.mel.HideSelectedObjects()
        pc.select(sl)
        
        # create Dom light
        pc.mel.redshiftCreateDomeLight()
        dom = pc.ls(sl=True)[0]
        pc.editRenderLayerAdjustment(dom.background_enable)
        dom.background_enable.set(0)
        pc.editRenderLayerAdjustment(dom.volumeNumSamples)
        dom.volumeNumSamples.set(256)
        
        # turn off all sample overrides in global render settings
        pc.setAttr("redshiftOptions.volumeSamplesOverrideEnable", 0)
        pc.setAttr("redshiftOptions.lightSamplesOverrideEnable", 0)
        pc.setAttr("redshiftOptions.AOSamplesOverrideEnable", 0)
        pc.setAttr("redshiftOptions.refractionSamplesOverrideEnable", 0)
        pc.setAttr("redshiftOptions.reflectionSamplesOverrideEnable", 0)
        
        # turn off GI
        pc.setAttr("redshiftOptions.primaryGIEngine", 0)
        pc.setAttr("redshiftOptions.secondaryGIEngine", 0)
        
        # turn off all AOVs
        for aov in pc.ls(type=pc.nt.RedshiftAOV):
            aov.enabled.set(0)
        pc.inViewMessage(message='<hl>Setup successful<hl>', position='midCenter', fade=True)
        
    def removeMatte(self):
        for item in self.matteBox.selectedItems():
            self.matteBox.takeItem(self.matteBox.row(item))