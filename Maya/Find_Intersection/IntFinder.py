"""
The module contains all the necessary Qt based classes to draw the plugin UI
and make calls to the intFind module
"""
#--------------------------------------------
# Name:         intFind.py
# Purpose:      Managing and drawing multiple instances intersection finding
#               plugin
# Author:       Hussain Parsaiyan
# License:      GPL v3
# Created       15/09/2012
# Copyright:    (c) ICE Animations. All rights reserved
# Python Version:   2.6
#--------------------------------------------
from plugins.utilities import *
from PyQt4 import QtGui, QtCore
import pymel.core as pc
import time, itertools as it
import maya.OpenMaya as om
import random, string

Qt = QtCore.Qt


class Item(QtGui.QStandardItem):

    def __init__(self , text, parent = None, addChild = True):
        """
        @param text: The name of the item/mesh
        @param parent: The parent Item of this QStandardItem
        @param addChild: Whether to add default child. i.e.: "Check self, too,
                         for self intersections"
        """

        super(Item,self).__init__(text)#'text' is the text that is displayed
        self.parent = parent
        self.setCheckable(True)
        if addChild:
            self.giveChild(0, Item("Self-Itersections too",
                            parent = self, addChild = False))
        self.fg = QtGui.QBrush()
        self.fg.setColor(Qt.yellow)
        self.setForeground(self.fg)

    def updateState(self):
        before_update = self.checkState()
        cumulative_child = self.childStates([self.child(x)
                                            for x in xrange(self.rowCount())])
        if before_update == Qt.Checked:
            if cumulative_child in [Qt.PartiallyChecked, Qt.Unchecked]:
                self.setCheckState(Qt.PartiallyChecked)
        else:
            if cumulative_child == Qt.Checked:
                self.setCheckState(Qt.Checked)
            elif cumulative_child == Qt.PartiallyChecked:
                self.setCheckState(Qt.PartiallyChecked)


    def childStates(self, childs):
        #If all Items are checked Qt.Checked
        #If all Items not checked Qt.Unchecked
        #Else Qt.PartiallyChecked
        #@param child List of Items
        #@return: aggregate of all the Items in the list

        uniqueStates = set([x.checkState() for x in  childs])
        if len(uniqueStates) > 1:
            return Qt.PartiallyChecked
        return uniqueStates.pop()

    def updateChildsTo(self, state, childs):
        #Sets all the Item in the childs list to state
        #@param state: The state to set to
        #@param childs: list of Item
        [x.setCheckState(state) for x in childs]

    def toggle(self, item):
        """
        This functionality is implemented by defualt therefore not needed.
        Code coverage for this can be zero.
        """
        if item.checkState() in [Qt.PartiallyChecked, Qt.Checked]:
            item.setCheckState(Qt.PartiallyChecked if item.checkState() == Qt.Checked else Qt.Checked )
        else: item.setCheckState(Qt.Checked)

    def giveChild(self, row, item):
        #appends a child, *item*, to self and sets self to tristate

        try:
            assert self.isCheckable()
            self.setChild(row, item)
            self.setTristate(True)
        except:
            print "Cannot append child at %s"%self.text()

class Model(QtGui.QStandardItemModel):

    def __init__(self, parent = None):
        super(Model, self).__init__(parent)
        self.itemChanged.connect(self.update)
        self.itemChanged.connect(self.setFindButtonState)

    def update(self, item):
        #A slot function, called when an Item, *item* is change
        #i.e. check/unchecked

        #to disable the function from being signaled when the parent is updated
        self.itemChanged.disconnect(self.update)

        parent = item.parent
        if parent and not isinstance(parent, gui):
            parent.updateState()
        item.updateChildsTo(item.checkState(),
                            [item.child(x)
                            for x in xrange(item.rowCount())])

        #to reestablish the connection
        self.itemChanged.connect(self.update)

    def setFindButtonState(self):
        #check the state of all the items in the model
        #if any item is partially or fully checked
        #enable the find button in the GUI
        partially_checked = filter(None, [True
                                        if self.item(x).checkState( )
                                            ==
                                            QtCore.Qt.PartiallyChecked
                                            else None
                                            for x in xrange(self.rowCount())])
        checked = filter(None,
                        [True if self.item(x).checkState() == Qt.Checked
                                else None for x in xrange(self.rowCount())])
        len_p, len_c = len(partially_checked),len(checked)
        if len_c >=1: self.parent().find.setEnabled(True)
        elif len_p > 1: self.parent().find.setEnabled(True)
        else: self.parent().find.setEnabled(False)


def createClass(*arg):
    #This function is used to dynamically create the GUI class
    #@param: arg[0]: The directory in which this module exists
    #@param: arg[1]: The UI class
    #@param: arg[2]: The base class QMainWindow
    class GUI(arg[1], arg[2]):

        def __init__(self, parent = getMayaWindow()):
            #parent: The main maya window
            super(GUI, self).__init__()
            self.setupUi(self)
            parent.addDockWidget(Qt.DockWidgetArea(0x2),self)
            # contains a flat set of intersections edge and face mixed.
            # Used for the sake of efficiency.
            self.intSelection = set()
            self.updateMeshView(first = True)
            self.makeConnections()

            #stamps the time at which the object was created
            self.creationTime = time.time()

            #*sceneSelection* contains the selection the user has manually
            #made in the scene.
            #These will be populated only when the user hits the Find key
            self.sceneSelection = []
            self.approxIntCount = 0
            self.accuEdgeCount = 0
            self.accuFaceCount =0
            self.pluginDir = arg[0]
            self.oddInt = set()
            #key: edge, value: face it intersects with
            #contains the proper mapping
            #from the edge to the face it intersects with.
            self.intDict = dict()
            pc.loadPlugin("%s\intFind.mll"%self.pluginDir, qt = True)#r"""C:\Documents and Settings\hussain.parsaiyan\My Documents\Visual Studio 2010\Projects\marylin\x64\Release\marylin.mll""") #

        def updateMeshView(self, first = False, complete = False):
            #@param first: Whether it is the first time the function is called
            #@param complete: [bool] whether all the meshes in scene are to be
            #                           list or just the selected ones
            if not first: del self.meshModel

            self.meshModel = Model(self)
            allMeshes = pc.ls(type="mesh", visible = True, ni= True)

            #adding the meshes to the tree view
            meshes = [Item(mesh.fullPath(), parent = self)
                        for mesh in
                            pc.ls(visible = True,
                                    type = "mesh",
                                    ni = True, sl = True)]
            [x.setCheckState(Qt.Checked) for x in meshes]

            #making sure the selected faces are already checked
            mesh_from_selected_transform = [mesh for transform in
                                                pc.ls(type = "transform",
                                                sl  = True)
                                            for mesh in
                                                transform.getShapes(ni = True)
                                            if isinstance(mesh, pc.nt.Mesh)
                                                and
                                                mesh in allMeshes]
            mesh_item_from_selected_transform = [Item(mesh.fullPath(),
                                                    parent = self)
                                                for mesh in
                                                mesh_from_selected_transform]
            [x.setCheckState(Qt.Checked)
                for x in mesh_item_from_selected_transform]
            meshes += mesh_item_from_selected_transform
            [x.updateChildsTo(x.checkState(),
                [x.child(y) for y in xrange(x.rowCount())]) for x in meshes]

            if complete:
                #to list down meshes from unselected transforms
                unselected_transform = [Item(mesh.fullPath(), parent = self)
                                        for transform in
                                            pc.ls(type = "transform")
                                        for mesh in
                                            transform.getShapes(ni = True)
                                        if mesh not in
                                            mesh_from_selected_transform
                                            and
                                            mesh in allMeshes
                                            and
                                            mesh not in
                                            pc.ls(type = "mesh",
                                                    sl = True,
                                                    visible = True,
                                                    ni = True)]
                meshes += unselected_transform
            #x{
            #to purge the mesh that have no history or edges
            itm =[]
            for item in xrange(len(meshes)):
                try:
                    pc.PyNode(meshes[item].text()).numEdges()
                except:
                    itm.append(item)
            #x}
            meshes = [meshes[x] for x in xrange(len(meshes)) if x not in itm]

            self.meshModel.appendColumn(meshes)
            self.meshes.setModel(self.meshModel)
            self.meshModel.setFindButtonState()
            self.sceneSelection = pc.ls(sl = True)
            self.userSelectionSelectedInScene = True
            self.revertSelection.setEnabled(False)
            self.intSelection.clear()

        def listAll(self):
            #calls updateMeshView to list all meshes
            self.updateMeshView(complete = True)

        def makeConnections(self):

            self.updateSelection.clicked.connect(self.updateMeshView)
            self.find.clicked.connect(self.findClicked)
            self.revertSelection.clicked.connect(self.revertClicked)
            self.accu.clicked.connect(self.accuToggled)
            self.listAllButton.clicked.connect(self.listAll)

        def accuToggled(self):

            #Slot function. Signaled when the Accurate Check button is checked

            if self.accu.checkState() == Qt.Checked:
                self.intCountLabel.setText(' '.join([x.capitalize()
                                            if x[0] == "n" else x
                                            for x in
                                        self.intCountLabel.text().split()[1:]
                                        ])) if self.intCountLabel.text()[0]\
                                        ==\
                                        "A" else None
                try:
                    if self.accuIntCount:
                        pass
                except:
                    odd = self.IAmMrOdd(self.intDict)
                    self.accuIntCount = sum([len(self.intDict[x])
                                    for x in self.intDict]) + len(odd)

                disInt = self.accuIntCount

            else:
                self.intCountLabel.setText(("Approx. "  +
                                    self.intCountLabel.text())\
                                    if self.intCountLabel.text()[0] =="N"\
                                    else self.intCountLabel.text())
                disInt = self.approxIntCount

            disEgde, disFace = self.accuEdgeCount, self.accuFaceCount
            self.intCount.display(disInt)
            self.edgeCount.display(disEgde)
            self.faceCount.display(disFace)

        def findClicked(self):

            #This function all finds determines
            #which EDGE intersects which face
            self.setEnabled(False)
            try:
                combinations = list(
                                it.permutations(
                                    [self.meshModel.item(x).text()
                                        for x in
                                        xrange(self.meshModel.rowCount()) if
                                    self.meshModel.item(x).checkState() in
                                    [Qt.Checked, Qt.PartiallyChecked]],
                                    2)
                            ) +\
                            filter(None,
                                [tuple(it.repeat(
                                    self.meshModel.item(x).text(),
                                    2))
                                    if
                                    self.meshModel.item(x).checkState()
                                    == Qt.Checked
                                    else None
                                    for x in xrange(
                                    self.meshModel.rowCount())
                                ]
                            )
                if combinations:
                    self.oddInt.clear()
                    self.intDict.clear()
                    facesChecked = 0
                    self.intCount.display(0)
                    self.edgeCount.display(0)
                    self.faceCount.display(0)
                    self.updateProgress(0)

                    try:
                        del self.accuIntCount
                    except:
                        pass

                    #key:mesh name , value: number of edges it contains
                    meshEdge = dict()

                    for mesh in combinations:
                        meshEdge[mesh[0]] = pc.PyNode(mesh[0]).numEdges()

                    tot_edges = sum([meshEdge[combination[0]]
                                for combination in combinations])
                                # the sum of all edges in the predator mesh

                    #find the name of the variable which contains the object
                    #figures it out by matching it
                    #with its own unique timestamp
                    g = globals()
                    thisObjectName = ""
                    for name in g:
                        if isinstance(g[name], type(self)):
                            if g[name].creationTime == self.creationTime:
                                thisObjectName =\
                                    __name__ + "."\
                                    +name
                    for combination in combinations:

                        try:
                            t1 = time.time()
                            pc.intFind(combination[0], combination[1],
                                        "%s.update_intDict" %thisObjectName)
                            print "Time taken to find intersections %s" %(time.time() - t1)
                            self.intCount.display(sum([len(self.intDict[x])
                                                        for x
                                                        in self.intDict]))
                            facesChecked += meshEdge[combination[0]]
                            self.updateProgress(facesChecked/
                                                float(tot_edges) * 90)
                        except:
                            print """intFind plugin not loaded.
                                    Trying to load......"""
                            try:
                                pc.loadPlugin("%s/intFind.mll" %self.pluginDir)#r"""C:\Documents and Settings\hussain.parsaiyan\My Documents\Visual Studio 2010\Projects\marylin\x64\Release\marylin.mll""")#
                            except:
                                print """Could not load/find
                                    intFind plugin at %s""" %self.pluginDir
                            #self.deleteLater()
                    #populates the *intSelection* set
                    self.intSelect(self.intDict)
                    self.revertClicked(True)
                    self.approxIntCount = sum([len(self.intDict[x])
                                                for x in self.intDict])\
                                                +len(set(self.oddInt))
                    self.accuEdgeCount= len(self.intDict.keys())
                    self.accuFaceCount = len(set([y for x in self.intDict
                                            for y in self.intDict[x]]
                                            + [x for x in self.oddInt]))
                    self.accuToggled()
                    self.updateProgress(100)

                else:
                    #There is a rare possibility of this getting covered
                    #since the Find button is disabled incase of no selection
                    print "Make a selection first"

            except:

                print "An error occured" #log this error somewhere

            self.setEnabled(True)

        def intSelect(self, intDict):

            #populates *intSelection*
            if intDict: #are there any intersections?
                self.intSelection.clear()
                for x in intDict:
                    self.intSelection.add(x)
                    [self.intSelection.add(y) for y in intDict[x]]
                [self.intSelection.add(y)
                                for y in self.oddInt]
            else:
                self.intSelection.clear()

            self.revertSelection.setEnabled(True
                                    if self.intSelection else False)

        def revertClicked(self, byFind = False):


            if byFind:#was this function called by findClicked
                if self.userSelectionSelectedInScene:
                    pc.sceneSelection = pc.ls(sl = True)
                pc.select([x for x in self.intSelection])

            else:
                if self.userSelectionSelectedInScene:
                    pc.select([x for x in self.intSelection])
                else:
                    pc.select(self.sceneSelection)

            self.userSelectionSelectedInScene =\
                            self.userSelectionSelectedInScene == False


        def update_intDict(self, edge , face):
            if edge != 0:
                edgeKey = self.intDict.get(edge)
                if edgeKey:
                    edgeKey.append(face)
                else:
                    self.intDict[edge] = [face]
            else:
                self.oddInt.add(face)

        def IAmMrOdd(self, intDict = None):

            #Explanation to the function neededs
            #r = list()
            if not intDict: intDict = self.intDict
            return [face for combination in it.combinations(intDict.keys(),2)
                        if combination[0].split(".")[0]
                            == combination[1].split(".")[0]
                        for face in self.getEdgeConnectedFace(combination[0])
                        if face in self.getEdgeConnectedFace(combination[1])
                        for intFace in intDict[combination[0]]
                        if intFace in intDict[combination[1]]]
            #the code below took too long to execute hence translated to OpenMaya
            #got 11x speed improvement
            #return [face.name() for combination in it.combinations(intDict.keys(),2)
                        #if combination[0].split(".")[0] ==
                        #combination[1].split(".")[0]
                        #for face in
                        #pc.PyNode(combination[0]).connectedFaces()
                        #if pc.MeshFace(unicode(face)) in
                            #pc.PyNode(combination[1]).connectedFaces()
                        #for intFace in intDict[combination[0]]
                        #if intFace in intDict[combination[1]]]
            #for combination in it.combinations(intDict.keys(),2):
                #for face in pc.PyNode(combination[0]).connectedFaces():
                    #if pc.MeshFace(face) in pc.PyNode(
                                    #combination[1]).connectedFaces():
                        #for intFace in intDict[combination[0]]:
                            #if intFace in intDict[combination[1]]:
                                #r.append(face)
            #return r
            #combinations =[(predator, prey)]
            #self.completer = QtGui.QCompleter(self.meshModel, self)
            #self.completer.highlighted.connect(self.prnt)
            #self.completer.setCompletionRole(QtCore.Qt.DisplayRole)
            #self.completer.setCompletionMode(
                #QtGui.QCompleter.PopupCompletion)
            #self.search.setCompleter(self.completer)
            #self.completer.setCaseSensitivity(
                #self.sensitive_search.checkState
                #if self.sensitive_search.checkState == 0 else 1)
            #self.sensitive_search.stateChanged.connect(
                #self.changeSensitivity)
        #def prnt(self, text):
            #print text
            #print self.completer.currentIndex()

        #def changeSensitivity(self, sensitive):
            #self.completer.setCaseSensitivity(sensitive
                    #if sensitive == 0 else 1)

        def updateProgress(self, value):
            #Updates the progress bar to a certain value, *value*, smoothly
            #@param value: [int] Value to move the progress bar to

            value = int(value)
            for x in xrange(self.pBar.value()
                                        if self.pBar.value() <= value
                                        else 0 ,
                                        value +1):
                #loop placed to make the progress look seamless and smooth
                self.pBar.setValue(x)
                time.sleep(0.01)

        def getEdgeConnectedFace(self, edge):
            #OpenMaya implemention to get the faces connected to an Edge
            #@param edge: Name identity of the edge

            selList = om.MSelectionList()
            selList.add(edge)
            meshDag = om.MDagPath()
            multiEdgeComp = om.MObject()
            selList.getDagPath(0, meshDag, multiEdgeComp)
            meit = om.MItMeshEdge(meshDag, multiEdgeComp)
            array = om.MIntArray()
            faceList = om.MScriptUtil().createIntArrayFromList([], array)
            meit.getConnectedFaces(array)
            return [".".join([edge.split(".")[0],"f[%s]" %face])
                    for face in array]

    return GUI

def intFind(*arg):

    #Helper function which, if, takes inputs
    #and create a global class which can
    #later have multiple instances
    #@param arg[0]: Directory of the module
    #@param arg[1]: Ui_MainWindow
    #@param arg[2]: QMainWindow. The base class
    if len ( arg ) == 3:
        global gui
        pDir = arg[0]
        gui = createClass(*arg)
    while True:
        rand = "".join(random.sample(string.ascii_letters,10))
        uiName = __name__ + "." + rand
        if uiName not in globals():
            exec('global {0}; {0} = gui(); {0}.show()'.format(rand))
            print uiName
            break