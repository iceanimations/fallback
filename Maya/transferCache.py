import pymel.core as pc
import uiContainer
from PyQt4.QtGui import QMessageBox, QApplication
import msgBox

def showMessage(**kwargs):
    return msgBox.showMessage(QApplication.activeWindow(), 'Error', **kwargs)

def transferCache(startFrame=None):
    if not startFrame:
        showMessage(msg='Start frame not specified',
                    icon=QMessageBox.Information)
    errors = {}
    meshes = pc.ls(sl=True)
    if not meshes:
        pc.warning('No selection found in the scene')
    for mesh in meshes:
        try:
            shape = mesh.getShape(ni=True)
        except AttributeError as ae:
            errors[mesh.name()] = str(ae)
            continue
        try:
            cache = shape.history(type='cacheFile')[0]
        except IndexError as ie:
            errors[mesh.name()] = 'No cache applied on %s'%mesh.name()
            continue
        try:
            cache.startFrame.set(startFrame)
        except Exception as ex:
            errors[mesh.name()] = str(ex)
            break
    if errors:
        details = '\n\n'.join(['\nReason: '.join([key, value]) for key, value in errors.items()])
        showMessage(msg='Errors occurred while transfering cache in out',
                        details=details,
                        icon=QMessageBox.Information)