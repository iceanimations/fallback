import os.path as osp
import logging
import iutil

from Qt.QtWidgets import (
        QDialog, QFileDialog, QMessageBox, QFrame, QMenu, QPushButton,
        QApplication, QWidgetAction, QAction, QCheckBox, QLayout, QSizePolicy)
from Qt.QtCompat import loadUi
from Qt.QtCore import Signal, QObject, Qt, QRect, QSize, QPoint

try:
    import tacticCalls as tc
    import imaya
    reload(tc)
    reload(imaya)
except:
    pass

try:
    import qtfy_maya_window as qtify
except:
    pass

reload(iutil)

rootPath = osp.dirname(__file__)
uiPath = osp.join(rootPath, 'ui')
iconPath = osp.join(rootPath, 'icons')


def setup_ui(uifile, base_instance=None):
    """Load a Qt Designer .ui file and returns an instance of the user interface
    Args:
        uifile (str): Absolute path to .ui file
        base_instance (QWidget): The widget into which UI widgets are
        loaded
    Returns:
        QWidget: the base instance
    """
    ui = loadUi(uifile)  # Qt.py mapped function
    if not base_instance:
        return ui
    else:
        for member in dir(ui):
            if not member.startswith('__') and \
                    member != 'staticMetaObject':
                setattr(base_instance, member, getattr(ui, member))
    return ui


class SingleInputBox(QDialog):
    '''
    This class offers a modal text field to enter a string or number
    '''

    def __init__(self,
                 parent=None,
                 title='Input',
                 label='Value',
                 browseButton=False,
                 fileFilter="*.fbx"):
        super(SingleInputBox, self).__init__(parent)
        loadUi(osp.join(uiPath, 'singleInputBox.ui'), self)
        self.setWindowTitle(title)
        self.label.setText(label)
        self.inputValue = ''
        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.cancel)
        self.inputBox.returnPressed.connect(self.ok)
        self.fileFilter = fileFilter
        if not browseButton:
            self.browseButton.hide()
        self.browseButton.clicked.connect(self.setFilename)

    def setFilename(self):
        filename = QFileDialog.getOpenFileName(self, 'Select File', '',
                                               self.fileFilter)
        if filename:
            self.inputBox.setText(filename)

    def getValue(self):
        return self.inputValue

    def ok(self):
        self.inputValue = self.inputBox.text()
        self.accept()

    def cancel(self):
        self.reject()


class SelectionBox(QDialog):
    '''
    This class offers a dialog offering multiple buttons such as QRadioButton
    or QCheckBox
    '''

    def __init__(self, parent=None, items=None, msg=''):
        '''
        @param items: objects of QCheckbox or QRadioButton
        '''
        super(SelectionBox, self).__init__(parent)
        loadUi(osp.join(uiPath, 'selectionBox.ui'), self)

        self.setMessage(msg)
        self.okButton.clicked.connect(self.ok)

        self.selectedItems = []
        self.items = items
        for item in items:
            self.itemsLayout.addWidget(item)

    def setCancelToolTip(self, tip):
        self.cancelButton.setToolTip(tip)

    def setMessage(self, msg):
        self.msgLabel.setText(msg)

    def ok(self):
        if not [item for item in self.items if item.isChecked()]:
            showMessage(
                self,
                title='Items Selection',
                msg='Please select at least one item',
                icon=QMessageBox.Information)
            return
        self.selectedItems = [
            item.text() for item in self.items if item.isChecked()
        ]
        self.accept()

    def getSelectedItems(self):
        return self.selectedItems


class MultiSelectComboBox(QFrame):
    '''
    This class offers comboBox to select multiple objects at once
    '''
    selectionDone = Signal(list)

    def __init__(self, parent=None, msg='--Select--', triState=False):
        super(MultiSelectComboBox, self).__init__(parent)
        loadUi(osp.join(uiPath, 'multiSelectComboBox.ui'), self)

        self.triState = triState
        self.msg = msg
        self.menu = QMenu(self)
        self.menu.setStyleSheet("QMenu { menu-scrollable: 1; }")
        self.button.setMenu(self.menu)

        self.menu.hideEvent = self.menuHideEvent
        self.setHintText(self.msg)

    def addDefaultWidgets(self):
        button = QPushButton('Invert Selection', self)
        button.clicked.connect(self.invertSelection)
        checkableAction = QWidgetAction(self.menu)
        checkableAction.setDefaultWidget(button)
        self.menu.addAction(checkableAction)
        btn = self.addItem('Select All')
        btn.clicked.connect(lambda: self.toggleAll(btn))
        self.menu.addSeparator()

    def invertSelection(self):
        for cBox in self.getWidgetItems():
            cBox.setChecked(not cBox.isChecked())
        self.toggleSelectAllButton()

    def toggleAll(self, btn):
        for cBox in self.getWidgetItems():
            cBox.setCheckState(btn.checkState())

    def toggleSelectAllButton(self):
        flag = True
        for cBox in self.getWidgetItems():
            if not cBox.isChecked():
                flag = False
                break
        for action in self.menu.actions():
            if type(action) == QAction:
                continue
            widget = action.defaultWidget()
            if widget.text() == 'Select All':
                widget.setChecked(flag)

    def setHintText(self, text):
        self.button.setText(text)

    def menuHideEvent(self, event):
        items = self.getSelectedItems()
        if items:
            s = ''
            if len(items) > 2:
                s = ',...'
            self.button.setText(','.join(items[:2]) + s)
        else:
            self.setHintText(self.msg)
        if event:
            QMenu.hideEvent(self.menu, event)
        self.selectionDone.emit(items)

    def getSelectedItems(self):
        return [
            cBox.text().strip() for cBox in self.getWidgetItems()
            if cBox.isChecked()
        ]

    def getState(self):
        return {
            cBox.text().strip(): cBox.checkState()
            for cBox in self.getWidgetItems()
        }

    def getWidgetItems(self):
        return [
            cBox
            for cBox in [
                action.defaultWidget() for action in self.menu.actions()
                if not type(action) is QAction
            ]
            if cBox.text().strip() != 'Select All'
            and cBox.text().strip() != 'Invert Selection'
        ]

    def getItems(self):
        return [cBox.text().strip() for cBox in self.getWidgetItems()]

    def addItem(self, item, selected=False):
        checkBox = QCheckBox(item, self.menu)
        checkBox.setTristate(self.triState)
        if selected:
            checkBox.setChecked(True)
        checkableAction = QWidgetAction(self.menu)
        checkableAction.setDefaultWidget(checkBox)
        self.menu.addAction(checkableAction)
        return checkBox

    def appendItems(self, items, selected=None):
        self.addItems(items, selected=selected, clear=False)

    def addItems(self, items, selected=None, clear=True):
        items = sorted(items)
        if clear:
            self.clearItems()
        self.addDefaultWidgets()
        for item in items:
            sel = False
            if selected and item in selected:
                sel = True
            btn = self.addItem(item, sel)
            btn.clicked.connect(self.toggleSelectAllButton)
        if selected:
            self.menuHideEvent(None)

    def clearItems(self):
        self.menu.clear()
        self.setHintText(self.msg)


class TacticUiBase(object):
    '''
    This class contains useful methods to add selection boxes to any Window
    that requires TACTIC Project, Episode, Sequence and Shot selection.
    Just inherit that Window form this class and use call the required methods
    '''

    def setContext(self, pro, ep, seq):
        if pro:
            for i in range(self.projectBox.count()):
                if self.projectBox.itemText(i) == pro:
                    self.projectBox.setCurrentIndex(i)
                    break
        if ep:
            for i in range(self.epBox.count()):
                if self.epBox.itemText(i) == ep:
                    self.epBox.setCurrentIndex(i)
                    break
        if seq:
            for i in range(self.seqBox.count()):
                if self.seqBox.itemText(i) == seq:
                    self.seqBox.setCurrentIndex(i)
                    break

    def setServer(self):
        self.server, errors = tc.setServer()
        if errors:
            self.showMessage(
                msg=errors.keys()[0],
                icon=QMessageBox.Critical,
                details=errors.values()[0])

    def populateProjects(self):
        self.projectBox.clear()
        self.projectBox.addItem('--Select Project--')
        projects, errors = tc.getProjects()
        if errors:
            self.showMessage(
                msg=('Error occurred while retrieving the list of projects'
                     ' from TACTIC'),
                icon=QMessageBox.Critical,
                details=iutil.dictionaryToDetails(errors))
        if projects:
            self.projectBox.addItems(projects)

    def setProject(self, project):
        self.setBusy()
        try:
            imaya.addOptionVar(tc.projectKey, project)
        except:
            pass
        self.epBox.clear()
        self.epBox.addItem('--Select Episode--')
        if project != '--Select Project--':
            errors = tc.setProject(project)
            if errors:
                self.showMessage(
                    msg='Error occurred while setting the project on TACTIC',
                    icon=QMessageBox.Critical,
                    details=iutil.dictionaryToDetails(errors))
            self.populateEpisodes()
        self.releaseBusy()

    def populateEpisodes(self):
        self.setBusy()
        try:
            episodes, errors = tc.getEpisodes()
            if errors:
                self.showMessage(
                    msg='Error occurred while retrieving the Episodes',
                    icon=QMessageBox.Critical,
                    details=iutil.dictionaryToDetails(errors))
            self.epBox.addItems(episodes)
        except Exception as ex:
            self.releaseBusy()
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        finally:
            self.releaseBusy()

    def populateSequences(self, ep):
        imaya.addOptionVar(tc.episodeKey, ep)
        self.setBusy()
        try:
            self.seqBox.clear()
            self.seqBox.addItem('--Select Sequence--')
            if ep != '--Select Episode--':
                seqs, errors = tc.getSequences(ep)
                if errors:
                    self.showMessage(
                        msg='Error occurred while retrieving the Sequences',
                        icon=QMessageBox.Critical,
                        details=iutil.dictionaryToDetails(errors))
                self.seqBox.addItems(seqs)
        except Exception as ex:
            self.releaseBusy()
            self.showMessage(msg=str(ex), icon=QMessageBox.Critical)
        finally:
            self.releaseBusy()

    def getSequence(self):
        seq = self.seqBox.currentText()
        if seq == '--Select Sequence--':
            seq = ''
        return seq

    def getProject(self):
        pro = self.projectBox.currentText()
        if pro == '--Select Project--':
            pro = ''
        return pro

    def getEpisode(self):
        ep = self.epBox.currentText()
        if ep == '--Select Episode--':
            ep = ''
        return ep


class MessageBox(QMessageBox):
    '''
    Creates a custom message box to show orbitrary messages
    '''

    def __init__(self, parent=QApplication.activeWindow()):
        super(MessageBox, self).__init__(parent)
        loadUi(osp.join(uiPath, 'msgBox.ui'), self)

    def showEvent(self, event):
        self._parent = self.parentWidget()
        if self._parent and hasattr(self._parent, 'geometry'):
            geo = self.geometry()
            pgeo = self._parent.geometry()
            self.move(pgeo.x() + pgeo.width()/2 - geo.width()/2,
                      pgeo.y() + pgeo.height()/2 - geo.height()/2)
        event.accept()

    def closeEvent(self, event):
        self.deleteLater()


def showMessage(parent,
                title='Shot Export',
                msg='Message',
                btns=QMessageBox.Ok,
                icon=None,
                ques=None,
                details=None,
                **kwargs):

    if parent == 'maya':
        parent = qtify.getMayaWindow()

    mBox = MessageBox(parent)
    mBox.setWindowTitle(title)
    mBox.setText(msg)
    if ques:
        mBox.setInformativeText(ques)
    if icon:
        mBox.setIcon(icon)
    if details:
        mBox.setDetailedText(details)
    customButtons = kwargs.get('customButtons')
    mBox.setStandardButtons(btns)
    if customButtons:
        for btn in customButtons:
            mBox.addButton(btn, QMessageBox.AcceptRole)
    pressed = mBox.exec_()
    if customButtons:
        cBtn = mBox.clickedButton()
        if cBtn in customButtons:
            return cBtn
    return pressed


class _QProgressLogHandler(QObject, logging.Handler):
    appended = Signal(str)

    def __init__(self, parent):
        if self.__class__ == _QProgressLogHandler:
            raise TypeError('_QProgressLogHandler cannot be instantiated')
        logging.Handler.__init__(self)
        QObject.__init__(self, parent=parent)
        self._maxx = 0
        self._value = 0
        self._inProgress = False
        self.loggers = []

    def __del__(self):
        for logger in self.loggers:
            self.removeLogger(logger)

    def emit(self, record):
        try:
            if not self.checkProgress(record):
                self.appended.emit(self.format(record))
        except:
            pass

    def checkProgress(self, record):
        if record.msg.startswith('Progress'):
            splits = record.msg.split(':')
            try:
                val, maxx = (num.strip() for num in splits[2].split('of'))
                self.setProgress(int(val), int(maxx))
            except (IndexError, ValueError):
                pass
            return True
        elif record.msg.startswith('Max'):
            splits = record.msg.split(':')
            try:
                maxx = record.msg.split(':')[-1].strip()
                self.setMaximum(int(maxx))
            except (IndexError, ValueError):
                pass
            return True
        elif record.msg.startswith('Start'):
            try:
                name = record.msg.split(':')[1].strip()
                self.startProgress(name)
            except (IndexError):
                self.startProgress()
            return True
        elif record.msg.startswith('Done'):
            try:
                name = record.msg.split(':')[1].strip()
                self.stopProgress(name)
            except (IndexError):
                self.stopProgress()
            return True
        else:
            return False

    def startProgress(self, name=''):
        self._inProgress = name

    def stopProgress(self, name=''):
        self._inProgress = ''

    def setProgress(self, val, maxx):
        self._value = val
        self._maxx = maxx

    def setMaximum(self, maxx):
        self._maxx = maxx

    def addLogger(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        if logger not in self.loggers:
            self.loggers.append(logger)
            logger.addHandler(self)

    def removeLogger(self, logger):
        if logger in self.loggers:
            self.loggers.remove(logger)
            logger.removeHandler(self)

    def setLevel(self, level, setLoggerLevels=True):
        super(_QProgressLogHandler, self).setLevel(level)
        if setLoggerLevels:
            for logger in self.loggers:
                logger.setLevel(level)


class QProgressBarLogHandler(_QProgressLogHandler):
    def __init__(self, progressBar):
        super(QProgressBarLogHandler, self).__init__(self.progressBar)
        self.progressBar = progressBar

    def startProgress(self, val, maxx):
        self.progressBar.show()

    def stopProgress(self):
        self.progressBar.hide()

    def setProgress(self, val, maxx):
        self.progressBar.setValue(val)
        self.progressBar.setMaximum(maxx)
        self.progressBar.repaint()

    def setMaximum(self, maxx):
        self.progressBar.setMaximum(maxx)
        self.progressBar.repaint()


class QTextLogHandler(_QProgressLogHandler):
    def __init__(self, text, progressBar=None):
        super(QTextLogHandler, self).__init__(text)
        self.text = text
        self.text.setReadOnly(True)
        self.appended.connect(self.append)
        self.progressBar = progressBar

    def append(self, msg):
        self.text.append(msg)
        self.text.repaint()

    def setProgress(self, val, maxx):
        if self.progressBar:
            self.progressBar.setValue(val)
            self.progressBar.setMaximum(maxx)
            self.progressBar.repaint()

    def setMaximum(self, maxx):
        if self.progressBar:
            self.progressBar.setMaximum(maxx)
            self.progressBar.repaint()


class FlowLayout(QLayout):
    '''
    Reimplementation of QLayout to adjust the elements in the avaible width and
    height in the window while it is being resized
    '''

    def __init__(self, parent=None, margin=0, spacing=-1):
        self.mysuper = super(FlowLayout, self)
        super(FlowLayout, self).__init__(parent)
        self.itemList = []
        self.setContentsMargins(0, 0, 0, 0)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        self.mysuper.setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(
                QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()


# some usefull CSS
borderColor = '#252525'
flat = '\nborder-style: solid;\nborder-color: ' + \
    borderColor + ';\nborder-width: 1px;\nborder-radius: 0px;\n'
styleSheet = ('QComboBox {' + flat + '\nmin-height: 25;\nmin-width: 125}' +
              'QPushButton {' + flat + '\nheight: 23;\nwidth: 75;\n}\n' +
              'QPushButton:hover, QToolButton:hover ' +
              '{\nbackground-color: #353535;\nborder-style: ' +
              'solid;\nborder-color: #4876FF\n}' + 'QLineEdit {height: 23;' +
              flat + '}\n'
              'QToolButton {' + flat + '}' + 'QPlainTextEdit {' + flat + '}')
