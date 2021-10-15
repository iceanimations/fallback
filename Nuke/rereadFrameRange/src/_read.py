'''
Created on Sep 1, 2015

@author: qurban.ali
'''
import os

import nuke

from Qt.QtWidgets import QApplication, QMessageBox
from utilities import msgBox, appUsageApp

title = 'Reread Frame Range'
parent = QApplication.activeWindow()


def showMessage(**kwargs):
    msgBox.showMessage(parent, title, **kwargs)


def getFrameRange(files):
    frames = []
    minFrame = maxFrame = None
    for phile in files:
        parts = phile.split('.')
        if len(parts) == 3:
            frames.append(parts[1])
    if frames:
        frames = [int(frame) for frame in frames]
        minFrame = min(frames)
        maxFrame = max(frames)
    return [minFrame, maxFrame]


def read():
    nodes = nuke.selectedNodes('Read')
    if not nodes:
        showMessage(msg='No Read node found in the selection',
                    icon=QMessageBox.Information)
        return

    for node in nodes:
        filename = node.knob('file').getValue()
        if filename:
            filename = os.path.dirname(filename)
            if os.path.exists(filename):
                files = os.listdir(filename)
                files = [phile for phile in files
                         if os.path.isfile(os.path.join(filename, phile))]
                if files:
                    first, last = getFrameRange(files)
                    if first is not None:
                        node.knob('first').setValue(first)
                        node.knob('origfirst').setValue(first)
                    if last is not None:
                        node.knob('last').setValue(last)
                        node.knob('origlast').setValue(last)
    appUsageApp.updateDatabase('rereadFrameRange')
