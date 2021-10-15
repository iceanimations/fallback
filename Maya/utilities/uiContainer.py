import logging
import re
import site
import sys

uic = None
sip = None

def getPathsFromFileDialogResult(result):
    if result and isinstance(result, tuple):
        return result[0]
    return result


def _pg(fileDiagFunc):
    def _pathGetterWrapper(*args, **kwargs):
        return getPathsFromFileDialogResult(fileDiagFunc(*args, **kwargs))
    _pathGetterWrapper.__doc__ = fileDiagFunc.__doc__
    return _pathGetterWrapper


def setUicLoggingLevel(uic, level=logging.INFO):
    for uic_subm in ['.properties', '.uiparser']:
        logger = logging.getLogger(uic.__name__ + uic_subm)
        logger.setLevel(level)


def setSipApiVersion(sip, version=2):
    API_NAMES = [
        "QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl",
        "QVariant"
    ]
    API_VERSION = version
    for name in API_NAMES:
        sip.setapi(name, API_VERSION)


def setPyQt4():
    global uic, sip

    from PyQt4 import uic
    import sip

    setUicLoggingLevel(uic)
    setSipApiVersion(sip)


def setPySide():
    global uic, sip
    try:
        import PySide as PyQt4
        import PySide.QtCore as QtCore
        import PySide.QtGui as QtGui
        import pysideuic as uic
        import shiboken as sip
    except ImportError:
        import PySide2 as PyQt4
        import PySide2.QtCore as QtCore
        import PySide2.QtGui as QtGui
        import PySide2.QtWidgets as QtWidgets
        for widget in dir(QtWidgets):
            if not widget.startswith('_'):
                setattr(QtGui, widget, getattr(QtWidgets, widget))
        import pyside2uic as uic
        import shiboken2 as sip
    import uiLoader
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    uic.loadUiType = uiLoader.loadUiType
    sip.wrapinstance = sip.wrapInstance
    setUicLoggingLevel(uic)

    setattr(QtGui.QFileDialog, 'getOpenFileNameAndFilter',
            QtGui.QFileDialog.getOpenFileName)
    setattr(QtGui.QFileDialog, 'getOpenFileNamesAndFilter',
            QtGui.QFileDialog.getOpenFileNames)
    setattr(QtGui.QFileDialog, 'getSaveFileNameAndFilter',
            QtGui.QFileDialog.getSaveFileName)

    QtGui.QFileDialog.getOpenFileName = _pg(QtGui.QFileDialog.getOpenFileName)
    QtGui.QFileDialog.getOpenFileNames = _pg(
        QtGui.QFileDialog.getOpenFileNames)
    QtGui.QFileDialog.getSaveFileName = _pg(QtGui.QFileDialog.getSaveFileName)

    sys.modules["PyQt4"] = PyQt4
    sys.modules["PyQt4.QtCore"] = QtCore
    sys.modules["sip"] = sip
    sys.modules["PyQt4.uic"] = uic
    sys.modules["PyQt4.QtGui"] = QtGui


def _setPySide():
    try:
        setPySide()
    except ImportError:
        setPyQt4()


try:
    import pymel.core as pc
    version = int(re.search('\\d{4}', pc.about(v=True)).group())
    if version in range(2011, 2017):
        site.addsitedir(r"R:\Python_Scripts\maya" + str(version) + r"\PyQt")
        setPyQt4()
    else:
        _setPySide()
except ImportError:
    _setPySide()
