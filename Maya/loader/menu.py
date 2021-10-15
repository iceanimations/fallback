'''
This modules contains the structure of ICE's script menu that is drawn inside
Maya
'''

import pymel.core as pc
import json
import os
from command import command

OS_PATH = os.path


CUSTOM_PLUG_IN_PATH = 'r:/maya_plugins/%s'
MENU_NAME = 'ICE_Menu'
MENU = None
# spice = ['Scripts']


def add_path(new_path, env_var='MAYA_PLUG_IN_PATH'):
    '''Make sure that given path is included in the env variable'''
    paths = os.environ[env_var]
    paths = paths.split(';')
    if new_path not in paths:
        paths.append(new_path)
        os.environ[env_var] = ';'.join(paths)


def add_plugin_path():
    '''Add plugin path for the current version of maya'''
    plugin_path = CUSTOM_PLUG_IN_PATH % pc.about(v=True)
    add_path(plugin_path, 'MAYA_PLUG_IN_PATH')


def construct_menu(parent, structure=None):
    ''' Makes a menu given a structure '''
    if structure is None:
        structure = {}
    for item in sorted(structure):
        value = structure[item]
        retired = value.get('_retire', False)
        if not retired:
            leaf = value.get('_leaf', False)
            kwargs = {'parent': parent,
                      'label': item,
                      'ann': value.get('_annotation', "")}

            if leaf:
                try:
                    call = MENU.call(call=value['_call'])
                except Exception:
                    def call(*args):
                        'place holder function for no calls'
                        print 'Nothing to call', args

                kwargs['c'] = call

                pc.menuItem(**kwargs)

            else:

                kwargs['to'] = True
                construct_menu(pc.subMenuItem(**kwargs), value)


def create_menu(*args):
    '''Creates the menu in maya'''
    reload(command)
    global MENU
    MENU = command.Menu
    menu_title = 'ICE Scripts' #%(random.choice(spice))
    gMainWindow = pc.mel.eval('$tmpVar = $gMainWindow')
    if pc.menu(MENU_NAME, exists=True):
        pc.deleteUI(MENU_NAME)
    menu = pc.menu(MENU_NAME, parent=gMainWindow, label=menu_title,
                   to=True)

    with open(OS_PATH.join(OS_PATH.dirname(__file__), 'command', 'menu.json'), 'r') as f:
        menu_structure = json.load(f)

    construct_menu(menu, menu_structure)
    pc.menuItem(parent=menu, divider=True, to=True)
    # pc.menuItem(parent = menu,
    #             label = 'Search ..',
    #             command = lambda *arg: None,
    #             ann = 'Search the menu')
    pc.menuItem(parent = menu,
                label = 'Rebuild This Menu',
                command = create_menu,
                ann = 'This will reconstruct the entire menu')
    return menu


def startup():
    try:
        add_plugin_path()
    except Exception as e:
        pc.warning('Cannot add plugin path %r' % e)
    create_menu()
    #mayaStartup.start()

startup()
