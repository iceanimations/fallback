from site import addsitedir as asd
asd(r"r:/Pipe_Repo/Users/Hussain/utilities/TACTIC")
asd(r"d:/user_files/hussain.parsaiyan/Documents/trunk/work/tactic")
import util_test as util
reload(util)
import os.path as op
from pyasm.command import Command
from client.tactic_client_lib import TacticServerStub

class Server(Command):
    def execute(my):
        my.info = getattr(my, my.kwargs['function'])(*my.kwargs['args'])


    def get_snapshot_list(my, project):
        return util.get_project_snapshots(project)

    def map_filename_to_snapshot(my, snaps):

        f_to_snap = {}

        for snap in snaps:

            f_to_snap[op.normpath(util.filename_from_snap(snap, mode = 'client_repo')).lower()] = snap
        util.pretty_print(f_to_snap.keys())
        return f_to_snap

    def check_scene(my, proj, refs):


        # {ref_path: False(if ref uptodate)|path of upto date}
        status = {}

        snaps = my.get_snapshot_list(proj)
        snap_files = my.map_filename_to_snapshot(snaps)

        for ref in refs:
            cur_snap = snap_files[op.normpath(ref).lower()]
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

    def foo():
        import json
        return map_filename_to_snapshot([json.loads('{"is_synced": true, "status": null, "code": "SNAPSHOT00001608", "description": "No description", "process": "model", "timestamp": "2014-03-26 20:02:47.030325", "s_status": null, "repo": null, "is_current": true, "__search_key__": "sthpw/snapshot?code=SNAPSHOT00001608", "search_code": "incidental_girl_1_warsuit", "id": 1608, "is_latest": true, "revision": 0, "project_code": "dettol_3", "level_id": null, "lock_login": null, "snapshot_type": "file", "lock_date": null, "search_type": "vfx/asset?project=dettol_3", "metadata": null, "version": 1, "server": null, "label": null, "context": "model", "snapshot": "<snapshot timestamp=\\"Wed Mar 26 11:14:41 2014\\" context=\\"model\\" search_key=\\"vfx/asset?project=dettol_3&amp;code=incidental_girl_1_warsuit\\" login=\\"saqib.hussain\\" checkin_type=\\"strict\\">\\n  <file file_code=\\"FILE00003762\\" name=\\"incidental_girl_1_warsuit_model_v001.ma\\" type=\\"main\\"/>\\n</snapshot>\\n", "login": "saqib.hussain", "level_type": null, "search_id": 59, "column_name": "snapshot"}')])

