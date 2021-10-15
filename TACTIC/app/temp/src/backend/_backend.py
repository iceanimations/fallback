from site import addsitedir as asd
import pymel.core as pc
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")
asd(r"d:/user_files/hussain.parsaiyan/Documents/trunk/work/tactic")
import util
reload(util)
import os.path as op
def get_snapshot_list(project):
    return util.get_project_snapshots(project)

def map_filename_to_snapshot(snaps):

    f_to_snap = {}
    
    for snap in snaps:
        
        f_to_snap[op.normpath(util.filename_from_snap(snap, mode = 'client_repo')).lower()] = snap
    util.pretty_print(f_to_snap.keys())
    return f_to_snap

def reference_paths():
    '''
    @return: {refNode: path} of all level one scene references
    '''
    refs = {}
    for ref in pc.listReferences():
        refs[ref] = str(ref.path)
    return refs

def check_scene(proj):

    refs = reference_paths()

    # {ref_path: False(if ref stale)|path of upto date}
    status = {}
    
    snaps = get_snapshot_list(proj)
    snap_files = map_filename_to_snapshot(snaps)

    for ref in refs:
        cur_snap = snap_files[op.normpath(refs[ref]).lower()]
        process = cur_snap['process'].lower()
        context = cur_snap['context'].lower()
        search_type = cur_snap['search_type'].lower()
        version = cur_snap['version']
        search_code = cur_snap['search_code']
        status[ref] = False
        for snap in snaps:
            
            if (process == snap['process'].lower() and
                context == snap['context'].lower() and
                search_type == snap['search_type'].lower() and
                search_code == snap['search_code']):
                if snap['version'] > version:
                    status[ref] = util.filename_from_snap(snap, mode = 'client_repo')
                    version = snap['version']
                    
    return status

def change_ref(node, newPath):
    return node.load(newFile = newPath)

