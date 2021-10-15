import maya.OpenMayaUI as apiUI
import pymel.core as pc
import site
import uiContainer
from PyQt4 import QtGui, QtCore
from sip import wrapinstance as wrap

def getMayaWindow():
        """
        Get the main Maya window as a QtGui.QMainWindow instance
        @return: QtGui.QMainWindow instance of the top level Maya windows
        """
        ptr = apiUI.MQtUtil.mainWindow()
        if ptr is not None:
            return wrap(long(ptr), QtGui.QMainWindow)

def toQtObject(mayaName):
        """
        Convert a Maya UI path to a Qt object
        @param mayaName: Maya UI Path to convert
        (Ex: "scriptEditorPanel1Window|TearOffPane|scriptEditorPanel1|testButton" )
        @return: PyQt representation of that object
        """
        ptr = apiUI.MQtUtil.findControl(mayaName)

        if ptr is None:
            ptr = apiUI.MQtUtil.findLayout(mayaName)
        if ptr is None:
            ptr = apiUI.MQtUtil.findMenuItem(mayaName)
        if ptr is not None:
            return wrap(long(ptr), QtCore.QObject)
