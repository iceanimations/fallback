#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      javeria.farooq
#
# Created:     29/09/2012
# Copyright:   (c) javeria.farooq 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import pymel.core as pc
import os
import re

global f1
f1 = None

class myIntSlider():

    __attr__ = None


    def __init__(self, label='myIntSlider', cc=None,
                 bgc=None, value=1,  minValue=1, maxValue=100,**args):
        
        with pc.rowLayout(nc=3) as self.__rl__:
            self.__textf__ = pc.text(l=str(label), width=100)
            self.__intf__ = pc.intField()
            self.__ints__ = pc.intSlider()

            pc.intSlider(self.__ints__, e=1, cc=pc.Callback(self.__sliderCommand__),
                         minValue=int(minValue), maxValue=int(maxValue), value=int(value),
                         step=1, w=200)
            if bgc:
                pc.intField(self.__intf__,e=1,bgc=bgc, w=50)
            pc.intField (self.__intf__,e=1, cc=pc.Callback(self.__fieldCommand__),
                minValue=int(minValue), maxValue=int(maxValue), value=int(value),
                step=1)
            self.__cc__ = cc

    def getValue(self):
        return self.__ints__.getValue()

    def getVal(self):
        return self.__nums__.getValue()

    def setValue(self, val):
        self.__intf__.setValue(int(val))
        self.__ints__.setValue(int(val))
        if self.__attr__: self.__attr__.set(int(val))

    def setBackgroundColor(self, clr):
        return self.__intf__.setBackgroundColor(clr)

    def connectControl(self, attr):
        self.__attr__ = pc.Attribute(attr)
        pc.connectControl(self.__intf__, attr)
        pc.connectControl(self.__ints__, attr)

    def __fieldCommand__(self):
        val = self.__intf__.getValue()
        self.__ints__.setValue(val)
        if callable(self.__cc__):self.__cc__()

    def __sliderCommand__(self):

        val = self.__ints__.getValue()
        self.__intf__.setValue(val)
        if callable(self.__cc__):self.__cc__()

    def __getSequenceFiles__(self):
        filename, mat_name = connectedFileNodes(g_selectedGeo)
        # spliting filename into dir filename and fileext
        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        filename, filext = os.path.splitext(basename)
        # seperating filename from number
        res = re.match('^(.*)(\D)(\d*)$', filename)
        if not res:
            return None
        sequencePrefix = ''.join(res.groups()[:-1])
        # making match pattern for all the files in the sequence
        matchbase = '^' + sequencePrefix + '(\\d+)' + filext + '$'
        matchbase = matchbase.replace('.', '\\.')
        seqPattern = re.compile(matchbase)
        #getting all the files from the directory and check whose names match the
        # sequence pattern
        alldirbasenames = os.listdir(dirname)
        sequenceFiles = []
        nums = []
        for dbn in alldirbasenames:
            matchobj = seqPattern.match(dbn)
            if matchobj:
                nums.append(int(matchobj.groups()[0]))
                sequenceFiles.append(os.path.join(dirname, dbn ))
        return sequenceFiles, nums

def enableSequence(f, btn, k1 ):
    f.useFrameExtension.set(True)
    exprs = f.frameExtension.inputs(type='expression')
    if exprs: pc.delete(exprs)

    btn.setLabel('Set Key')
    btn.setCommand(pc.Callback(setKey, f, k1))

def deleteExpression(f, btn, k1):
    try:
        f = pc.nt.File(f)
    except TypeError:
        pc.error('The argument %s is not a file node' %f)
    except pc.MayaNodeError:
        pc.error('The argument %s is not a valid node' %f)

    exprs = f.frameExtension.inputs(type='expression')
    if exprs: pc.delete(exprs)

    btn.setLabel('Set Key')
    btn.setCommand(pc.Callback(setKey, f, k1))

def setKey(f, k1):
    """
    This function set the key on the file
    """
    try:
        f = pc.nt.File(f)
    except TypeError:
        pc.error('The argument %s is not a file node' %f)
    except pc.MayaNodeError:
        pc.error('The argument %s is not a valid node' %f)

    f.useFrameExtension.set(True)
    if f.frameExtension.inputs(type='expression'):
        f.frameExtension.disconnect()
    pc.setKeyframe(f + '.frameExtension', inTangentType="flat",  outTangentType="step")

def isLowres(path):
    dirname, fn1 = os.path.split(path)
    return os.path.basename(dirname) == 'low res'

def findLowresPath(filename):
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    changepath = os.path.join(dirname, 'low res')
    return os.path.join(changepath, basename)

def findHiresPath(filename):
    fn1 = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    parentDir = os.path.abspath(os.path.join(dirname, '..'))
    return os.path.join(parentDir, fn1)

def lowresExists(path):
    return os.path.exists(findLowresPath(path))

def hiresExists(path):
    return os.path.exists(findHiresPath(path))

def lowResFiles(f,btn):
    filename=pc.getAttr(f+".fileTextureName")
    # spliting filename into dir filename and fileext
    path=findLowresPath(filename)
    if os.path.exists(path):
        pc.setAttr(f+".fileTextureName",path)
    else:
        pc.error('Lowres path was not found')
    btn.setLabel('make HiRes')
    btn.setCommand(pc.Callback(highResFiles, f, btn))

def highResFiles(f,btn):
    filename=pc.getAttr(f+".fileTextureName")
    # spliting filename into dir filename and fileext
    newpath = findHiresPath(filename)
    if os.path.exists(newpath):
        pc.setAttr(f+".fileTextureName",newpath)
    else:
        pc.error('Hires path was not found')
    btn.setLabel('make LoRes')
    btn.setCommand(pc.Callback(lowResFiles, f, btn))

def isHires(path):
    dirname, fn1 = os.path.split(path)
    parentDir = os.path.abspath(os.path.join(dirname, '..'))

def getSequenceFiles(filename):
    # spliting filename into dir filename and fileext
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    filename, filext = os.path.splitext(basename)
    # seperating filename from number
    res = re.match('^(.*)(\D)(\d*)$', filename)
    if not res:
        return None
    sequencePrefix = ''.join(res.groups()[:-1])
    # making match pattern for all the files in the sequence
    matchbase = '^' + sequencePrefix + '(\\d+)' + filext + '$'
    matchbase = matchbase.replace('.', '\\.')
    seqPattern = re.compile(matchbase)
    #getting all the files from the directory and check whose names match the
    # sequence pattern
    alldirbasenames = os.listdir(dirname)
    sequenceFiles = []
    nums = []
    for dbn in alldirbasenames:
        matchobj = seqPattern.match(dbn)
        if matchobj:
            nums.append(int(matchobj.groups()[0]))
            sequenceFiles.append(os.path.join(dirname, dbn ))
    return sequenceFiles, nums

def range(file_name):
    """
    This funtion on the basis of file takes its range
    """
    filename=pc.getAttr(file_name+".fileTextureName")
    # spliting filename into dir filename and fileext
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)
    filename, filext = os.path.splitext(basename)
    # seperating filename from number
    res = re.match('^(.*)(\D)(\d*)$', filename)
    if not res:
        return None
    sequencePrefix = ''.join(res.groups()[:-1])
    # making match pattern for all the files in the sequence
    matchbase = '^' + sequencePrefix + '(\\d+)' + filext + '$'
    matchbase = matchbase.replace('.', '\\.')
    seqPattern = re.compile(matchbase)
    #getting all the files from the directory and check whose names match the
    # sequence pattern
    alldirbasenames = os.listdir(dirname)
    sequenceFiles = []
    nums = []
    for dbn in alldirbasenames:
        matchobj = seqPattern.match(dbn)
        if matchobj:
            nums.append(int(matchobj.groups()[0]))
        sequenceFiles.append(os.path.join(dirname, dbn ))
    try:
        numRange, sequenceFiles=(min(nums), max(nums)), sorted(sequenceFiles)
    except ValueError:
        numRange = None

    return numRange

def listingname(f,btn1,clmain,mattname,k1):
    global f1
    fname = f.fileTextureName.get()
    basename = os.path.basename(fname)
    dname = os.path.dirname(fname)
    if not isLowres(fname) and lowresExists(fname):
        dirname = os.path.join(dname, 'low res')
        filename=os.path.join(dirname, basename)
        seqFiles, nums = getSequenceFiles(filename)
        alldirbasenames = os.listdir(dirname)
        seq = sorted(zip(seqFiles, nums))
        with pc.frameLayout(label=mattname,collapsable=1,parent=clmain) as f1:
            with pc.rowColumnLayout(nc = 10):
                for bn, n in seq:
                    with pc.columnLayout():
                        pc.text(l=str(n))
                        pc.symbolButton(image=bn, w=50, h=50,c=pc.Callback(k1.setValue,n))
    elif isLowres(fname) or lowresExists(fname):
        seqFiles, nums = getSequenceFiles(fname)
        alldirbasenames = os.listdir(dname)
        seq = sorted(zip(seqFiles, nums))
        with pc.frameLayout(label=mattname,collapsable=1, parent=clmain) as f1:
            with pc.rowColumnLayout(nc = 10):
                for bn, n in seq:
                    with pc.columnLayout():
                        pc.text(l=str(n))
                        pc.symbolButton(image=bn, w=50, h=50,c=pc.Callback(k1.setValue,n))
    elif not isLowres(fname) and not lowresExists(fname):
        pc.warning('Low Res was not found, using hiRes instead! Please wait! ..')
        seqFiles, nums = getSequenceFiles(fname)
        alldirbasenames = os.listdir(dname)
        seq = sorted(zip(seqFiles, nums))
        with pc.frameLayout(label=mattname, collapsable=1, parent=clmain) as f1:
            with pc.rowColumnLayout(nc=10):
                for bn, n in seq:
                    with pc.columnLayout():
                        pc.text(l=str(n))
                        pc.symbolButton(image=bn, w=50, h=50,
                                c=pc.Callback(k1.setValue, n))
    return f1

def selectFileNode(f):
    pc.select(f)

def selectAllFileNode(args):
    file_name = g_sequenceFiles
    pc.select(cl=1)
    for f in file_name:
        pc.select(f,add=True)

def connectedFileNodes(mesh=[]):
    """
    This Funtion takes the file name of a particular mesh and return the filename
    """
    fileNodes = []
    materialNodes = []
    for meshNode in mesh:
        instNo = meshNode.instanceNumber()
        validIndices = meshNode.iog[instNo].og.get(mi=True)
        shadingEngines = set()

        if validIndices:
            for index in validIndices:
                newSet = set(meshNode.iog[instNo].og[index].outputs(type='shadingEngine'))
                shadingEngines.update(newSet)
        try:
            shadingEngines.update(meshNode.iog[instNo].outputs(type='shadingEngine'))
        except IndexError:
            pass
        for x in list(shadingEngines):
            shaders = x.surfaceShader.inputs()
            if shaders:
                s=shaders[0]
                sfiles = s.color.inputs(type='file')
                if sfiles:
                    fileNodes.append(sfiles[0])
                    materialNodes.append(s)
    return fileNodes, materialNodes

def displaySliders(clmain):
    global g_selectedGeo
    global g_sequenceFiles
    g_sequenceFiles = []
    g_selectedGeo = pc.ls(sl=True,type='geometry',dag=True)
    file_name, mat_name = connectedFileNodes(g_selectedGeo)
    d=[range(f) for f in file_name]
    with pc.columnLayout('cl1', parent=clmain) as cl1:
        for i, r in enumerate(d):
            if r is not None:
                with pc.rowLayout('rl'+str(i), nc=5):
                    f = file_name[i]
                    g_sequenceFiles.append(f)
                    mattname=mat_name[i]
                    k1 = myIntSlider(minValue=r[0], maxValue=r[1], value=1, label=mat_name[i])
                    k1.connectControl(f +'.frameExtension')
                    if not f.useFrameExtension.get():
                        btn1 = pc.button(label = 'Enable Sequence', w = 100)
                        btn1.setCommand(pc.Callback(enableSequence, f, btn1, k1))
                    elif f.frameExtension.inputs(type='expression'):
                        btn2 = pc.button(label = 'Delete Expression', w = 100)
                        btn2.setCommand(pc.Callback(deleteExpression, f, btn2, k1))
                    else:
                        btn3 = pc.button(label = 'Set Key', w = 100)
                        btn3.setCommand(pc.Callback(setKey, f, k1))
                    pc.button(label='select', c=pc.Callback(selectFileNode, f))
                    path = f.fileTextureName.get()
                    if isLowres(path) and hiresExists(path):
                        btn = pc.button(label='make HiRes')
                        btn.setCommand(pc.Callback(highResFiles,f, btn))
                    elif not isLowres(path) and lowresExists(path):
                        btn = pc.button(label='make LoRes')
                        btn.setCommand(pc.Callback(lowResFiles,f, btn))
                    elif isLowres(path):
                        pc.text(l=' lowRes only')
                    else:
                        pc.text(l=' HiRes only')
                    btn1=pc.button(label='Detail')
                    btn1.setCommand(pc.Callback(check,f,btn1,clmain,mattname,k1))
    return cl1

def deleteGUI(f1,btn1):
    pc.deleteUI(f1)

def check(f, btn1, clmain,mattname,k1):
    global f1
    if f1:
        deleteGUI(f1, btn1)
    f1=listingname(f,btn1,clmain,mattname,k1)

def refreshSliders(btn, clmain, cl1):
    global f1
    if f1:
        pc.deleteUI(f1)
        f1 = None
    pc.deleteUI(cl1)
    cl1 = displaySliders(clmain)
    btn.setCommand(pc.Callback(refreshSliders, btn, clmain, cl1))

def gui():
    """
    This function display the gui
    """
    if pc.window('Animate_Textures', exists=True):
        pc.deleteUI('Animate_Textures', window=True)
    with pc.window('Animate_Textures') as win :
        with pc.columnLayout(adj=True) as clmain:
            pc.text(l='')
            btn = pc.button(l='Refresh')
            pc.button(label='Select All',c=selectAllFileNode)
            pc.text(l='')
            cl1 = displaySliders(clmain)
            btn.setCommand(pc.Callback(refreshSliders, btn, clmain ,cl1))
    pc.showWindow(win)

def main():
    gui()

def animTexture():
    gui()

def help():
    pass

if __name__ == '__main__':
    main()

