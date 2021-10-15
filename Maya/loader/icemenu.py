'''
This modules contains the structure of ICE's script menu that is drawn inside
Maya
'''

import pymel.core as pc
import json
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import site
from command import command

OS_PATH = os.path

CUSTOM_PLUG_IN_PATH = 'r:/maya_plugins/%s'
MENU_NAME = 'ICE_Menu'
MENU_TITLE = 'Ice Scripts'
MENU = None
SITE_DIRS = [
    r"R:\Python_Scripts\plugins",
    r"R:\Python_Scripts\plugins\utilities",
    r"R:\Pipe_Repo\Projects\TACTIC",
    r"R:\Pipe_Repo\Projects\TACTIC\app",
    r"R:\Pipe_Repo\Users\Hussain\utilities"
]
# spice = ['Scripts']


def add_path(new_path, env_var='MAYA_PLUG_IN_PATH'):
    '''Make sure that given path is included in the env variable'''
    paths = os.environ[env_var]
    paths = paths.split(os.pathsep)
    if new_path not in paths:
        paths.append(new_path)
        os.environ[env_var] = os.pathsep.join(paths)


def add_plugin_path():
    '''Add plugin path for the current version of maya'''
    plugin_path = CUSTOM_PLUG_IN_PATH % pc.about(v=True)
    add_path(plugin_path, 'MAYA_PLUG_IN_PATH')

def add_site_dirs():
    '''Add site dirs to python environment'''
    for path in SITE_DIRS:
        site.addsitedir(path)


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
    gMainWindow = pc.mel.eval('$tmpVar = $gMainWindow')
    print(MENU_NAME)
    if pc.menu(MENU_NAME, exists=True):
        pc.deleteUI(MENU_NAME)
    menu = pc.menu(MENU_NAME, parent=gMainWindow, label=MENU_TITLE, to=True)

    with open(OS_PATH.join(OS_PATH.dirname(__file__), 'command', 'menu.json'),
              'r') as file_:
        menu_structure = json.load(file_)

    construct_menu(menu, menu_structure)
    pc.menuItem(parent=menu, divider=True, to=True)
    # pc.menuItem(parent = menu,
    #             label = 'Search ..',
    #             command = lambda *arg: None,
    #             ann = 'Search the menu')
    pc.menuItem(parent=menu,
                label='Rebuild This Menu',
                command=create_menu,
                ann='This will reconstruct the entire menu')
    return menu


def load_config(filename='loader.cfg'):
    '''read variables from a config file'''
    config_path = os.path.join(os.path.dirname(__file__), filename) 
    config_parser = configparser.RawConfigParser()
    config_parser.read(config_path)

    global CUSTOM_PLUG_IN_PATH
    try:
        CUSTOM_PLUG_IN_PATH = config_parser.get('Paths', 'CUSTOM_PLUG_IN_PATH')
        if not CUSTOM_PLUG_IN_PATH.endswith('%s'):
            CUSTOM_PLUG_IN_PATH = os.path.join(CUSTOM_PLUG_IN_PATH, '%s')
    except (configparser.NoOptionError, configparser.NoSectionError ):
        pass

    global MENU_NAME
    try:
        MENU_NAME = config_parser.get('Menu', 'name')
    except (configparser.NoOptionError, configparser.NoSectionError ):
        pass

    global MENU_TITLE
    try:
        MENU_TITLE = config_parser.get('Menu', 'title')
    except (configparser.NoOptionError, configparser.NoSectionError ):
        pass

    global SITE_DIRS
    try:
        _site_dirs = config_parser.get('Paths', 'site_dirs')
        SITE_DIRS = [path.strip() for path in _site_dirs.split(os.pathsep)]
    except (configparser.NoOptionError, configparser.NoSectionError ):
        pass


def dump_config(filename='loader.cfg'):
    '''Dump current variables to a config file'''
    config_path = os.path.join(os.path.dirname(__file__), filename) 
    config_parser = configparser.RawConfigParser()

    config_parser.add_section('Paths')
    config_parser.set('Paths', 'CUSTOM_PLUG_IN_PATH', CUSTOM_PLUG_IN_PATH)
    config_parser.set('Paths', 'SITE_DIRS', ';\n'.join(SITE_DIRS))
    config_parser.add_section('Menu')
    config_parser.set('Menu', 'name', MENU_NAME)
    config_parser.set('Menu', 'title', MENU_TITLE)

    with open(filename, 'w+') as _file:
        config_parser.write(_file)


def startup():
    ''' function startup '''
    load_config()
    try:
        add_plugin_path()
        add_site_dirs()
    except Exception as e:
        pc.warning('Cannot add plugin path %r' % e)
    create_menu()
    # mayaStartup.start()

startup()
