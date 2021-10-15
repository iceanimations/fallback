'''
Created on Mar 4, 2015

@author: qurban.ali
'''
import time
import nuke
import os
import os.path as osp

from Qt.QtWidgets import (
        QMessageBox, QFileDialog, QPushButton, QMainWindow, QApplication)
from Qt.QtCore import QThread
from Qt.QtCompat import loadUi

from utilities import msgBox, qutil, appUsageApp


__title__ = 'Auto Save'
__enable_key__ = 'enable'
__directory_key__ = 'directory'
__name_key__ = 'name'
__prompt_key__ = 'prompt'
__interval_key__ = 'interval'
__is_limited_key__ = 'isLimited'
__limit_key__ = 'limit'
__autosave_directory_name__ = 'Autosaves'
__prefs_file__ = osp.join(osp.expanduser('~'), '.nuke', 'autosavePrefs.txt')
__root_path__ = osp.dirname(osp.dirname(__file__))
__ui_path__ = osp.join(__root_path__, 'ui')


class SavePrefs(QMainWindow):
    def __init__(self, parent=QApplication.activeWindow()):
        super(SavePrefs, self).__init__(parent)
        loadUi(osp.join(__ui_path__, 'main.ui'), self)

        self.thread = Thread(self)

        self.testButton.released.connect(self.saveIncrement)
        self.saveButton.clicked.connect(self.savePrefs)
        self.currentDirectoryButton.toggled.connect(self.fillPath)
        self.userGuideAction.triggered.connect(self.showHelp)

        self.testButton.hide()
        self.saveButton.setFocus()
        self.saveButton.hide()

        directory = nuke.script_directory()
        if osp.basename(directory) == __autosave_directory_name__:
            directory = osp.dirname(directory)
        self.pathBox.setText(directory)
        name = nuke.root().name()
        if name != 'Root':
            self.nameBox.setText(
                    osp.splitext(osp.basename(name))[0].split('_')[0])

        self.startThread()

        appUsageApp.updateDatabase('AutoSave')

    def fillPath(self, val):
        if val:
            self.pathBox.setText(nuke.script_directory())

    def showHelp(self):
        self.showMessage(
                msg='Every option is self explanatory, adjust your\n' +
                'settings and check the "Enable" option to start the\n' +
                'autosave. Just make sure not to close the window,\n' +
                'minimize it. If you do close the window, autosave\n' +
                'won\'t work anymore')

    def showMessage(self, **kwargs):
        self.stopThread()
        btn = msgBox.showMessage(self, title=__title__, **kwargs)
        self.startThread()
        return btn

    def getDirectory(self):
        message = ''
        directory = self.pathBox.text()
        if not directory:
            message = 'Directory path not specified'
        if not osp.exists(directory):
            message = 'Specified path does not exist'
            directory = ''
        if message:
            self.showMessage(msg=message, icon=QMessageBox.Information)
        return directory

    def getScriptName(self):
        name = self.nameBox.text()
        if not name:
            self.showMessage(
                               msg='Could not retrieve current file name',
                               icon=QMessageBox.Information)
        return name

    def getEnabled(self):
        return self.enableButton.isChecked()

    def getPrompt(self):
        return self.promptButton.isChecked()

    def getSaveInterval(self):
        return self.intervalBox.value() * 60  # convert minutes to seconds

    def isLimited(self):
        return self.limitButton.isChecked()

    def getLimit(self):
        return self.limitBox.value()

    def setPathBox(self):
        filename = QFileDialog.getExistingDirectory(self, __title__,
                                                    self.getDirectory())
        if filename:
            self.pathBox.setText(filename)

    def saveIncrement(self):
        print 'Running...'
        if self.getEnabled():
            if self.getPrompt():
                btn = self.showMessage(
                        msg='Autosave is ready to save the current file',
                        ques='Do you want to proceed?',
                        icon=QMessageBox.Question,
                        btns=QMessageBox.Yes | QMessageBox.No)
                if btn == QMessageBox.No:
                    return
            directory = osp.join(self.getDirectory(),
                                 __autosave_directory_name__)
            filename = osp.splitext(self.getScriptName())[0]
            if not filename:
                return
            if not osp.exists(directory):
                try:
                    os.mkdir(directory)
                except Exception as ex:
                    self.showMessage(msg=str(ex),
                                     icon=QMessageBox.Information)
                    return
            version = filename+'_v001'
            files = os.listdir(directory)
            if files:
                if self.isLimited() and len(files) >= self.getLimit():
                    dontShowButton = QPushButton(
                            'Don\'t show again', self)
                    createVersionButton = QPushButton(
                            'Create new version', self)
                    overwriteLastButton = QPushButton(
                            'Overwrite last file', self)
                    btn = self.showMessage(
                        msg='Maximum limit for the autosaves has been reached',
                        ques='What do you want to do?',
                        icon=QMessageBox.Question,
                        btns=QMessageBox.Cancel,
                        customButtons=[createVersionButton,
                                       overwriteLastButton,
                                       dontShowButton])
                    if btn == dontShowButton:
                        self.limitButton.setChecked(False)
                        return
                    elif btn == overwriteLastButton:
                        tempVar = qutil.getLastVersion(directory, filename)
                        if tempVar:
                            version = tempVar
                            try:
                                os.remove(osp.join(directory, version+'.nk'))
                            except Exception as ex:
                                self.showMessage(
                                                   msg=str(ex),
                                                   icon=QMessageBox.Critical)
                                return
                    elif btn == createVersionButton:
                        tempVar = qutil.getLastVersion(
                                directory, filename, nxt=True)
                        if tempVar:
                            version = tempVar
                    else:
                        return
                else:
                    tempVar = qutil.getLastVersion(
                            directory, filename, nxt=True)
                    if tempVar:
                        version = tempVar
            # save the file
            nuke.scriptSaveAs(osp.join(directory, version+'.nk'))

    def saveData(self, data):
        try:
            with open(__prefs_file__, 'w') as f:
                f.write(str(data))
        except Exception as ex:
            self.showMessage(msg=str(ex),
                             icon=QMessageBox.Information)

    def getData(self):
        data = {}
        try:
            with open(__prefs_file__, 'r') as f:
                data.update(eval(f.read()))
        except Exception as ex:
            self.showMessage(msg=str(ex),
                             icon=QMessageBox.Information)
        return data

    def savePrefs(self):
        data = {}
        directory = self.getDirectory()
        if not directory:
            return
        name = self.getScriptName()
        if not name:
            return
        data[__enable_key__] = self.getEnabled()
        data[__prompt_key__] = self.getPrompt()
        data[__directory_key__] = directory
        data[__name_key__] = name
        data[__interval_key__] = self.getSaveInterval()
        data[__is_limited_key__] = self.isLimited()
        data[__limit_key__] = self.getLimit()
        self.saveData(data)
        self.statusBar().showMessage('Preferences saved...', 2000)

    def startThread(self):
        self.thread.start()

    def stopThread(self):
        self.thread.terminate()

    def closeEvent(self, event):
        self.stopThread()
        self.deleteLater()


class Thread(QThread):
    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)
        self.parentWin = parent

    def run(self):
        while 1:
            time.sleep(self.parentWin.getSaveInterval())
            self.parentWin.testButton.released.emit()
