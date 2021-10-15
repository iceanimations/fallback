import os
import nuke
import shutil

tempFile = os.path.join(os.path.expanduser('~'), 'renderArchive', 'log.txt')
log = ''
if not os.path.exists(os.path.dirname(tempFile)):
    os.mkdir(os.path.dirname(tempFile))


def ArchiveBeforeRender(args=None):
    nodee = args
    if not nodee:
        aNode = nuke.selectedNode()
    else:
        aNode = nodee
    allK = nuke.Node.knobs(aNode)
    available = allK.get('ArchiveButton')
    if available is None:
        return
    if nuke.Boolean_Knob.value(available):
        createArchive(aNode)
        nodee = None
    elif nuke.Boolean_Knob.value(available):
        pass


def removeExtraCallBacks():

    # print 'callback for ' , nuke.thisNode().name()
    archivefunctions = []
    for nodeClass, listcallbacks in nuke.callbacks.beforeRenders.items():
        if nodeClass != 'Write':
            break
            for callback in listcallbacks:
                if callback[0].func_name == 'ArchiveBeforeRender':
                    archivefunctions.append(callback[0])

    # print  'archive functions ', archivefunctions

    for func in archivefunctions:
        nuke.callbacks.removeBeforeRender(func, nodeClass='Write')


createArchive1 = '''
import os
import nuke
import sys
import shutil
import time

def copyFile(srcc, destt):
    try:
        shutil.copyfile(srcc, destt)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)

s = ""
nodee = None
nn = nuke.selectedNode()
if not nodee:
    n = nuke.selectedNode()
    s = n.knob('file').getValue()
    if s:
        s = os.path.dirname(s).replace('/', '\\\\')

else:

    s = nodee.knob('file').getValue()
    if s:
        s = os.path.dirname(s).replace('/', '\\\\')

# creating the directory here
if s and os.path.exists(s):
    if os.listdir(s):
        # checking for present archives
        archive_dir = []
        for d in os.listdir(s):
            dirc = os.path.join(s,d)
            if os.path.isdir(dirc) and d[:7] == 'Archive':
                archive_dir.append(d)


        default_directory = 'Archive_0001'


        #in case of no present archives create a new one
        if not archive_dir:

            dirname = default_directory
            dest = os.path.join(s,dirname)
            os.mkdir(dest)
            print 'file created'

            #else proceed to create archives


        else:
            #print archive_dir
            archive_dir.sort()
            #print archive_dir
            dirname = archive_dir[-1]
            dirname = dirname[8:]
            sname = int(dirname) + 1
            newName = 'Archive_' + str(sname).zfill(4)
            dest = os.path.join(s,newName)
            os.mkdir(dest)


            # moving all files in that directory

        for f in os.listdir(s):
            src = os.path.join(s,f)
            #print src
            if os.path.isfile(src):
                d = os.path.join(dest,f)
                copyFile(src,d)

        print "File copied to the arcive directory"


        for f in os.listdir(s):
            src = os.path.join(s,f)
            if os.path.isfile(src) and (f.endswith('.png') or f.endswith('.jpg')):
                os.remove(src)

        nodee = None
'''


def modifyWrite():
    n = nuke.thisNode()

    knobName1 = 'ArchiveButtonPy'
    knobName = 'ArchiveButton'
    if knobName not in nuke.Node.knobs(n):
        n.addKnob(nuke.Boolean_Knob(knobName, 'Archive'))
        n.addKnob(nuke.PyScript_Knob(knobName1, 'Archive', createArchive1))
        n.addKnob(nuke.Text_Knob("divider", ""))
    allK = nuke.Node.knobs(n)
    RenderKnob = allK.get('Render')
    n.addKnob(RenderKnob)

    #print "button created"

    with open(tempFile, 'w') as f:
        f.write(log)


def setupNuke():
    nuke.addOnCreate(modifyWrite, nodeClass='Write')
    values = nuke.callbacks.beforeRenders.values()
    if not values:
        nuke.callbacks.addBeforeRender(ArchiveBeforeRender, nodeClass='Write')


def copyFile(srcc, destt):
    try:
        shutil.copyfile(srcc, destt)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)


def createArchive(args=None):

    s = ""
    nodee = args
    nn = nuke.selectedNode()
    if not nodee:
        n = nuke.selectedNode()
        s = n.knob('file').getValue()
        if s:
            s = os.path.dirname(s).replace('/', '\\\\')

    else:

        s = nodee.knob('file').getValue()
        if s:
            s = os.path.dirname(s).replace('/', '\\\\')

    # creating the directory here
    if not s or not os.path.exists(s): return
    if not os.listdir(s): return
    # checking for present archives
    archive_dir = []
    for d in os.listdir(s):
        dirc = os.path.join(s, d)
        if os.path.isdir(dirc) and d[:7] == 'Archive':
            archive_dir.append(d)

    default_directory = 'Archive_0001'

    #in case of no present archives create a new one
    if not archive_dir:

        dirname = default_directory
        dest = os.path.join(s, dirname)
        os.mkdir(dest)
        print 'file created'

        #else proceed to create archives

    else:
        #print archive_dir
        archive_dir.sort()
        #print archive_dir
        dirname = archive_dir[-1]
        dirname = dirname[8:]
        sname = int(dirname) + 1
        newName = 'Archive_' + str(sname).zfill(4)
        dest = os.path.join(s, newName)
        os.mkdir(dest)

        # moving all files in that directory

    for f in os.listdir(s):
        src = os.path.join(s, f)
        #print src
        if os.path.isfile(src):
            d = os.path.join(dest, f)
            copyFile(src, d)

    print "File copied to the arcive directory"

    for f in os.listdir(s):
        src = os.path.join(s, f)
        if os.path.isfile(src) and (f.endswith('.png') or f.endswith('.jpg')):
            os.remove(src)

    nodee = None
