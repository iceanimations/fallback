import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
import qtify_maya_window as qtfy
from uiContainer import uic
import pymel.core as pc
import os.path as osp
import appUsageApp
reload(appUsageApp)

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Name(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Name, self).__init__(parent)
        self.setupUi(self)
        
        self.renameButton.clicked.connect(self.name)
        self.prefixBox.returnPressed.connect(self.name)
        self.sgtomtlButton.clicked.connect(self.sgtomtl)
        
        appUsageApp.updateDatabase('nameMtl')
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def getUniqueName(self, name):
        cnt = 1
        while pc.objExists(name):
            name += str(cnt)
            cnt += 1
        return name
        
    def sgtomtl(self):
        meshes = pc.ls(sl=True, dag=True, type='mesh')
        if not meshes:
            pc.warning('No selection found for meshes')
            return
        sgs = set()
        for mesh in meshes:
            sgs = sgs.union(set(mesh.outputs(type='shadingEngine')))
        for sg in sgs: 
            try:
                mtl = sg.surfaceShader.inputs()[0]
                name = sg.name()
                pc.rename(sg, self.getUniqueName(name))
                pc.rename(mtl, name)
            except IndexError:
                pc.warning('No mtl found for %s'%sg.name())
            except Exception as ex:
                pc.warning(str(ex))
                
        
    def name(self):
        prefix = str(self.prefixBox.text())
        if not prefix:
            pc.warning('Prefix not specified...')
            return
        meshes = pc.ls(sl=True, type='mesh', dag=True)
        if not meshes:
            pc.warning('No selection found for meshes')
            return
        sgs = set()
        for mesh in meshes:
            sgs = sgs.union(set(mesh.outputs(type='shadingEngine')))
        for sg in sgs:
            try:
                mtl = sg.surfaceShader.inputs()[0]
                name = mtl.name()
                pc.rename(sg, self.getUniqueName(prefix +'_'+ name))
            except IndexError:
                pc.warning('No mtl found on %s'%sg.name())
            except Exception as ex:
                pc.warning(str(ex))