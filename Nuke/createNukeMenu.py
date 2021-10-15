import nuke

import nukeMenuCommands
reload(nukeMenuCommands)

from nukeMenuCommands import (
        replaceReadPaths,
        fromRedToDefault,
        renderWrites,
        setNearestFrame,
        saveIncrement,
        addWriteNodes,
        reread,
        replaceBackdropCameras,
        renderThreads,
        selectErrorNodes,
        replaceRenderLayers,
        rebuildMenu
        )

import startup
startup.setupNuke()

# add new script to the following dict
# key => name of the script that will appear in the nuke under ICE Scripts menu
# value => name of the function to be called when user clicks that menu item
# finally create that function in the nukeMenuCommands.py

nukeMenu = {
            'Backdrop Tool': [replaceReadPaths, 'Ctrl+Alt+B'],
            'Red to Default': [fromRedToDefault, 'Ctrl+Alt+D'],
            'Batch Render': [renderWrites, 'Ctrl+Alt+R'],
            'Set Nearest Frame': [setNearestFrame, 'Ctrl+Alt+N'],
            'Auto Increment Save': [saveIncrement, 'Ctrl+Alt+I'],
            'Add Write Node': [addWriteNodes, 'Ctrl+Alt+W'],
            'Reread Frame Range': [reread, 'Ctrl+Alt+F'],
            'Replace Cameras In Backdrops': [replaceBackdropCameras,
                                             'Ctrl+Alt+C'],
            'Render Threads': [renderThreads, ''],
            'Select Error Nodes': [selectErrorNodes, ''],
            'Replace Render Layer': [replaceRenderLayers, ''],
}

menuName = 'ICE Scripts/'


def create():
    nuke.menu('Nuke').removeItem(menuName[0:-1])
    for name, func in nukeMenu.items():
        nuke.menu('Nuke').addCommand(menuName+name, func[0], func[1])
    nuke.menu('Nuke').menu(menuName[0:-1]).addSeparator()
    nuke.menu('Nuke').addCommand(menuName+'Rebuild this Menu', rebuildMenu)
