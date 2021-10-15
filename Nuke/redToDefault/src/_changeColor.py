import nuke
from Qt.QtWidgets import QApplication, QMessageBox

from utilities import msgBox, appUsageApp


def change(msg=True):
    nodes = nuke.selectedNodes('Read')
    if msg:
        if not nodes:
            msgBox.showMessage(
                    QApplication.activeWindow(),
                    title='Red To Default',
                    msg='No Read node selected',
                    icon=QMessageBox.Information)
            return
    for node in nodes:
        node.knob('tile_color').setValue(0)

    appUsageApp.updateDatabase('RedToDefault')

    return True
