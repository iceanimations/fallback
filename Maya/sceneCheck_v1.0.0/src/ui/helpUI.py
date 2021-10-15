# Embedded file name: c:\sceneCheck_v1.0.0/src/ui\helpUI.py
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Ui_Dialog(QDialog):

    def __init__(self, parent = None):
        super(Ui_Dialog, self).__init__(parent)
        self.setObjectName('Dialog')
        self.resize(585, 441)
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName('gridLayout')
        spacerItem = QSpacerItem(574, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 3)
        self.textBrowser = QTextBrowser(self)
        palette = QPalette()
        brush = QBrush(QColor(60, 59, 58))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush = QBrush(QColor(224, 223, 222))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush)
        self.textBrowser.setPalette(palette)
        self.textBrowser.setAutoFillBackground(False)
        self.textBrowser.setFrameShape(QFrame.NoFrame)
        self.textBrowser.setObjectName('textBrowser')
        self.gridLayout.addWidget(self.textBrowser, 1, 0, 1, 3)
        spacerItem1 = QSpacerItem(479, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 2)
        self.pushButton = QPushButton(self)
        self.pushButton.setMinimumSize(QSize(91, 27))
        self.pushButton.setMaximumSize(QSize(91, 27))
        self.pushButton.setObjectName('pushButton')
        self.gridLayout.addWidget(self.pushButton, 2, 2, 1, 1)
        QMetaObject.connectSlotsByName(self)
        self.setWindowTitle(QApplication.translate('Dialog', 'Dialog', None, QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QApplication.translate('Dialog', '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;">\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600;">Maya Scene Check v1.0.0</span></p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Requirements: PyQt 4.8.2 and Sip 4.15.4</span></p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Tested with Maya 2014 x64 on Centos6 and Win7 x64</p>\n<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"></p>\n<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; font-style:italic;">The sceneCheck is designed to catch common issues before file publish and conform assets to the Barajoun pipeline. It will also run Maya\'s \'optimize scene\' in some cases. </span></p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; font-style:italic;">This script should be run anytime before a file is sent to Barajoun.</span></p>\n<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Usage</span>:</p>\n<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">    1. select one of the presets on the lower left</p>\n<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">    2. hit \'scene check\'</p>\n<p align="justify" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"> </p>\n<p align="justify" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">After a while you\'ll either get a \'Scene seems to be clean\' message or a list of objects with issues. When clicking any of the objects on the left, you\'ll get the nature of the problem on the right. </p>\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"> </p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600;">Here\'s the list of checks that will run in each category:</span></p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">modelling</span> -&gt; delete (references, cameras, history, non static channels); Freeze transformation top hierarchy; negative and no uvs; polycleanup; maya scene cleanup; shell; conform normal</p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">texturing </span>-&gt; delete (references, cameras, history, non static channels); negative and no uvs; missing textures; non arnold shaders assigned; maya scene cleanup; conform normal</p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">cloth &amp; hair</span> -&gt; delete (references, cameras); negative and no uvs; non arnold shaders assigned; conform normal</p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">rigging</span> -&gt; delete (references, cameras); non arnold shaders assigned</p>\n<p style="-qt-paragraph-type:empty; margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"></p>\n<p style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Copyright (c) Barajoun Entertainment</span></p>\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:8pt;">Developed by Domingos Silva</span></p></body></html>', None, QApplication.UnicodeUTF8))
        self.pushButton.setText(QApplication.translate('Dialog', 'Close', None, QApplication.UnicodeUTF8))
        return

    def showUI(self):
        self.exec_()