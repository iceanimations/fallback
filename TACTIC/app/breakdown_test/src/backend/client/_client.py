from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")
asd(r"d:/user_files/hussain.parsaiyan/Documents/trunk/work/tactic")
import util_test as util
reload(util)

import pymel.core as pc

def reference_paths():
    '''
    @return: {refNode: path} of all level one scene references
    '''
    refs = {}
    for ref in pc.listReferences():
        refs[ref] = str(ref.path)
    return refs


def change_ref(node, newPath):
    return node.load(newFile = newPath)

def check_scene(proj):

    print util.get_server().execute_cmd('app.breakdown_test.src.backend.server.Server', {'function': 'check_scene', 'args': (proj, reference_paths().values())})

def foo():
    print util.get_server().execute_cmd('app.breakdown_test.src.backend.server.Server', {'abc': 'def'})
