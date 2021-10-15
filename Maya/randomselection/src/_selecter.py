'''
Created on Apr 10, 2014

@author: qurban.ali
'''
import site
site.addsitedir(r"R:\Pipe_Repo\Users\Qurban\utilities")
from uiContainer import uic
from PyQt4.QtGui import *
import qtify_maya_window as qtfy
import appUsageApp
import os.path as osp
import random
import time
import pymel.core as pc


Form, Base = uic.loadUiType(r'%s\ui\window.ui'%osp.dirname(osp.dirname(__file__)))
class Window(Form, Base):
    def __init__(self, parent = qtfy.getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)
        
        self.selectionSet = {}
        
        self.createButton.clicked.connect(self.create)
        self.setsBox.activated.connect(self.select)
        self.clearButton.clicked.connect(self.clear)
        
        # update the database, how many times this app is used
        appUsageApp.updateDatabase('randomSelection')
        
    def closeEvent(self, event):
        self.deleteLater()
        
    def create(self):
        self.clear()
        selection = set(pc.ls(sl=True, type='mesh', dag=True))
        if not selection:
            pc.warning('No selection found')
            return
        divider = int(self.numberBox.value())
        totalNum = len(selection)
        if divider > totalNum:
            pc.warning('Number of sets cann\'t be greater than total number of meshes')
            return
        num = int(totalNum/divider)
        i = 1
        while selection:
            newNum = len(selection)
            if num > newNum:
                self.selectionSet['Selection '+ str(i-1)].update(selection)
                break
            newSet = set(random.sample(selection, num))
            item = 'Selection '+ str(i)
            self.setsBox.addItem(item)
            self.selectionSet[item] = newSet
            selection = selection.difference(newSet)
            i += 1
        self.msgLabel.setText(str(divider) +' sets created')
        qApp.processEvents()
        time.sleep(2)
        self.msgLabel.setText('')
        
    def clear(self):
        self.setsBox.clear()
        self.setsBox.addItem('--Select Set--')
        self.selectionSet.clear()
    
    def select(self):
        text = str(self.setsBox.currentText())
        if text == '--Select Set--':
            return
        if self.selectionSet.has_key(text):
            pc.select(self.selectionSet[text])