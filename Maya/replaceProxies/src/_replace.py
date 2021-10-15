'''
Created on Jul 11, 2018

@author: qurban.ali
'''

import re
import pymel.core as pc
import os.path as osp
import auth.user as user
import iutil
import app.util as util


def replace():
    try:
        server = user.get_server()
        server.set_project('suntop_s02')
        all_assets = server.eval("@SOBJECT(vfx/asset['asset_category', 'vegetation'])")
        all_asset_codes = set([asset['code'] for asset in all_assets])
        all_proxies = {node: set(iutil.splitPath(node.fileName.get())) for node in pc.ls(type=pc.nt.RedshiftProxyMesh) if node.fileName.get()}
        
        for node, path in all_proxies.items():
            asset_code = list(all_asset_codes.intersection(path))
            print asset_code
            if len(asset_code) == 1:
                asset = [ast for ast in all_assets if ast['code'] == asset_code[0]]
                if asset:
                    asset = asset[0]
                    context = re.search('model|shaded', osp.join(*path))
                    if context:
                        context = context.group()
                        snap = server.get_snapshot(asset, context=context, version=-1, include_paths_dict=1)
                        if snap:
                            path = snap.get('__paths_dict__').get('rs')
                            if path:
                                node.fileName.set(util.translatePath(path[0]))
                            else: print 'rs not found'
                        else: print 'snap not found'
                    else: print 'context not found'
                else: print 'asset not found'
            else: print 'more than one matching assets'
    except Exception as ex:
        print str(ex)