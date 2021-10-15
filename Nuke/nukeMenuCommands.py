import sys

import nuke

import createNukeMenu


def replaceReadPaths():
    import replaceReadPath as rrp
    reload(rrp)
    rrp.Window().show()


def fromRedToDefault():
    import redToDefault as rd
    reload(rd)
    rd.change()


def renderWrites():
    import renderWrite
    reload(renderWrite)
    renderWrite.render()


def rebuildMenu():
    reload(createNukeMenu)
    createNukeMenu.create()


def setNearestFrame():
    for node in nuke.selectedNodes('Read'):
        node.knob('on_error').setValue(3)


def saveIncrement():
    import autoSave
    reload(autoSave)
    autoSave.Window().show()


def addWriteNodes():
    import addWrite
    reload(addWrite)
    addWrite.addWrite()


def reread():
    import rereadFrameRange as rr
    reload(rr)
    rr.read()


def replaceBackdropCameras():
    import replaceCamera
    reload(replaceCamera)
    print replaceCamera.replaceBackdropCameras()


def renderThreads():
    from renderthreads import renderthreads
    reload(renderthreads)
    renderthreads.run()


def selectErrorNodes():
    from errorNodes import main, error_nodes, error_nodes_ui
    reload(error_nodes)
    reload(error_nodes_ui)
    reload(main)
    main.main_gui()


def replaceRenderLayers():

    for key in sys.modules.keys():
        if key.startswith('replaceRenderLayer'):
            del sys.modules[key]

    import replaceRenderLayer
    win = replaceRenderLayer.win()
    win.show()
