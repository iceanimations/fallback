import pymel.core as pc


import site
from genericpath import exists
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
import qtify_maya_window as qtfy
from uiContainer import uic
import os.path as osp

root_path = osp.dirname(osp.dirname(__file__))
ui_path = osp.join(root_path, 'ui')

Form, Base = uic.loadUiType(osp.join(ui_path, 'main.ui'))
class Remover(Form, Base):
    def __init__(self, parent=qtfy.getMayaWindow()):
        super(Remover, self).__init__(parent)
        self.setupUi(self)
        
        self.removeButton.clicked.connect(self.remove)
        
    def remove(self):
        text = str(self.nameBox.text())
        if not pc.namespace(exists=text):
            pc.warning("Namespace doesn't exist")
            return
        pc.namespace(mergeNamespaceWithRoot=True,
                     removeNamespace=text)
        
    def closeEvent(self):
        self.deleteLater()