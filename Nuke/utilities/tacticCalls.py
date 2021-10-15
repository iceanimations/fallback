'''
Created on Oct 30, 2015

@author: qurban.ali
'''

import os
import iutil.symlinks as symlinks
from auth import user
import tactic_client_lib as tcl
import qutil
import os.path as osp
import re
from collections import Counter
try:
    import maya.cmds as cmds
    import pymel.core as pc
    import addKeys
except:
    pass
import iutil
import app.util as util
from pprint import pprint

try:
    pc.mel.eval(
        "source \"R:/Pipe_Repo/Users/Hussain/utilities/loader/command/mel/addInOutAttr.mel\";"
    )
except:
    pass

server = None
# define keys for optionVar and fileInfo
projectKey = 'tacticProjectKey'
episodeKey = 'tacticEpKey'
sequenceKey = 'tacticSeqKey'
shotKey = 'tacticShotKey'
contextKey = 'tacticContextKey'

class CCounter(Counter):
    def update_count(self, c):
        for key, value in c.items():
            self[key] = value if self[key] < value else self[key]


def uploadShotToTactic(path):
    errors = []
    mappings = {}
    '''uploads cache, preview and camera to Tactic from a given shot path exported by multiShotExport'''
    try:
        if osp.exists(path):
            if server:
                shot = osp.basename(path)
                sk = None
                try:
                    sk = server.eval("@SOBJECT(vfx/shot['code', '%s'])" %
                                     shot)[0]['__search_key__']
                except IndexError:
                    errors.append('Could not find %s on TACTIC' % shot)
                except Exception as ex:
                    errors.append(str(ex))
                if sk:
                    contexts = os.listdir(path)
                    for context in contexts:
                        contextPath = osp.join(path, context)
                        if osp.isdir(contextPath):
                            files = os.listdir(contextPath)
                            if files:
                                if context == 'JPG':
                                    cont = 'animation/preview/JPG'
                                else:
                                    cont = 'animation/' + context
                                snapshot = server.create_snapshot(sk,
                                                                  cont)['code']
                                types = ['main' for _ in files]
                                server.add_file(
                                    snapshot,
                                    [osp.join(contextPath, f) for f in files],
                                    mode='copy',
                                    file_type=types)
                            else:
                                errors.append('Unable to export files for %s' %
                                              osp.basename(contextPath))
                        else:
                            pass
                            #errors.append('%s is not a directory'%contextPath)
                    if not contexts:
                        errors.append('Nothing found to export')
            else:
                errors.append('Could not find TACTIC server')
    except Exception as ex:
        errors.append(str(ex))
    return '\n'.join(errors)


def setServer(serv=None, project=None):
    errors = {}
    global server
    if serv:
        server = serv
        return
    try:
        if user.user_registered():
            server = user.get_server()
        else:
            user.login('tactic', 'tactic123')
            server = user.get_server()
            if not project:
                project = 'test_mansour_ep'
            server.set_project(project)
    except Exception as ex:
        errors['Could not connect to TACTIC'] = str(ex)
    return server, errors


def getProjects():
    errors = {}
    projects = []
    if server:
        try:
            projects = server.eval("@GET(sthpw/project.code)")
        except Exception as ex:
            errors['Could not get the list of projects'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ''
    return projects, errors


def setProject(project):
    errors = {}
    if project:
        if server:
            try:
                server.set_project(project)
            except Exception as ex:
                errors['Could not set the project'] = str(ex)
        else:
            errors['Could not find the TACTIC server'] = ''
    return errors


def getEpisodes():
    eps = []
    errors = {}
    if server:
        try:
            eps = server.eval("@GET(vfx/episode.code)")
        except Exception as ex:
            errors['Could not get the list of episodes from TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return eps, errors


def getShotPath(shot):
    path = ''
    errors = {}
    if server:
        try:
            path = server.get_virtual_snapshot_path(
                server.query('vfx/shot', filters=[('code', shot)]),
                context='animation')
            if path:
                path = util.translatePath(path)
        except Exception as ex:
            errors['Could not get the shot Path from TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return iutil.dirname(path, 3), errors


def getSequences(ep):
    seqs = []
    errors = {}
    if server:
        if ep:
            try:
                seqs = server.eval(
                    "@GET(vfx/sequence['episode_code', '%s'].code)" % ep)
            except Exception as ex:
                errors[
                    'Could not get the list of sequences from TACTIC'] = str(
                        ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return seqs, errors


def getShots(seq):
    shots = {}
    errors = {}
    if server:
        try:
            shts = server.query('vfx/shot', filters=[('sequence_code', seq)])
            for shot in shts:
                shots.update({ shot['code']: [shot['frame_in'], shot['frame_out']]})
        except Exception as ex:
            errors['Could not get the list of Shots from TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return shots, errors


def getFrameRange(shot):
    frameRange = []
    errors = {}
    if server:
        try:
            shot = server.eval("@SOBJECT(vfx/shot['code', '%s'])" % shot)[0]
            frameRange[:] = [shot['frame_in'], shot['frame_out']]
        except Exception as ex:
            errors['Could not get the list of Shots from TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return frameRange, errors


def getLatestFile(file1, file2):
    latest = file1
    if os.path.getmtime(file2) > os.path.getmtime(file1):
        latest = file2
    return latest


def getAssetsInEp(ep):
    errors = {}
    assets = []
    try:
        assets[:] = server.eval(
            "@GET(vfx/asset_in_episode['episode_code', '%s'].asset_code)" % ep)
    except Exception as ex:
        errors[
            'Could not retrieve the list of asset in selected Episode'] = str(
                ex)
    return assets, errors


def assetsInSeq(seq):
    seqAssets = None
    errors = {}
    try:
        seqAssets = server.eval(
            "@GET(vfx/asset_in_sequence['sequence_code', '%s'].asset_code)" %
            seq)
    except Exception as ex:
        errors['Could not retrieve assets from TACTIC for %s' % seq] = str(ex)
    return seqAssets, errors


def getAssetsInSeq(ep, seq):
    assets = {}
    errors = {}
    if server:
        try:
            maps = symlinks.getSymlinks(
                server.get_base_dirs()['win32_client_repo_dir'])
        except Exception as ex:
            errors['Could not retrieve the maps from TACTIC'] = str(ex)
        seqAssets = None
        try:
            seqAssets = server.eval(
                "@GET(vfx/asset_in_sequence['sequence_code', '%s'].asset_code)"
                % seq)
        except Exception as ex:
            errors['Could not retrieve assets from TACTIC for %s' %
                   seq] = str(ex)
        if not seqAssets:
            errors['No Asset found in %s' % seq] = ''
        epAssets = []
        try:
            epAssets[:] = server.query(
                'vfx/asset_in_episode',
                filters=[('asset_code', seqAssets), ('episode_code', ep)])
        except Exception as ex:
            errors['Could not retrieve asset from TACTIC for %s' %
                   ep] = str(ex)
        if not epAssets:
            errors['No published Assets found in %s' % ep] = ''
        else:
            for epAsset in epAssets:
                try:
                    snapshot = server.get_snapshot(
                        epAsset,
                        context='rig',
                        version=0,
                        versionless=True,
                        include_paths_dict=True)
                    context = 'rig'
                except Exception as ex:
                    errors['Could not get the Snapshot from TACTIC for %s' %
                           epAsset['asset_code']] = str(ex)
                if not snapshot:
                    snapshot = server.get_snapshot(
                        epAsset,
                        context='model',
                        version=0,
                        versionless=True,
                        include_paths_dict=True)
                    context = 'model'
                if not snapshot:
                    snapshot = server.get_snapshot(
                        epAsset,
                        context='shaded',
                        version=0,
                        versionless=True,
                        include_paths_dict=True)
                    context = 'shaded'
                if snapshot:
                    paths = snapshot['__paths_dict__']
                    if paths:
                        newPaths = None
                        if paths.has_key('maya'):
                            newPaths = paths['maya']
                        elif paths.has_key('main'):
                            newPaths = paths['main']
                        else:
                            errors[
                                'Could not find a Maya file for %s' % epAsset[
                                    'asset_code']] = 'No Maya or Main key found'
                        if newPaths:
                            if len(newPaths) > 1:
                                assets[epAsset['asset_code']] = [
                                    context,
                                    symlinks.translatePath(
                                        getLatestFile(*newPaths), maps)
                                ]
                            else:
                                assets[epAsset['asset_code']] = [
                                    context,
                                    symlinks.translatePath(newPaths[0], maps)
                                ]
                        else:
                            errors[epAsset[
                                'asset_code']] = 'No Maya file found'
                    else:
                        errors[epAsset[
                            'asset_code']] = 'No Paths found to a file'
    else:
        errors['Could not find the TACTIC server'] = ""
    return assets, errors


def getAssetsInShot(shots):
    assets = []
    errors = {}
    if server:
        try:
            assets[:] = server.query(
                'vfx/asset_in_shot', filters=[('shot_code', shots)])
        except Exception as ex:
            errors['Could get the list assets in shots'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return assets, errors


def addAssetsToShot(assets, shot):
    errors = {}
    if server:
        data = [{'asset_code': asset, 'shot_code': shot} for asset in assets]
        try:
            server.insert_multiple('vfx/asset_in_shot', data)
        except Exception as ex:
            errors['Could not add Assets to TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return errors

def addShotLayer(layer, shot):
    tLayer = None
    errors = {}
    if server:
        try:
            tLayer = server.get_unique_sobject('vfx/layer', data={'name': layer, 'shot_code': shot})
        except Exception as ex:
            errors['Could not create new layer %s'%layer] = str(ex)
    else:
        errors['Could not get the TACTIC server'] = ''
    return tLayer, errors

def checkinRenders(sk, context, path, frameRange):
    errors = {}
    if server:
        try:
            snap = server.create_snapshot(sk, context)
            server.add_group(snap['code'], file_path=path, file_type='main', file_range=frameRange, mode='preallocate')
        except Exception as ex:
            errors['Could create snapshot or add files to %s'%sk] = str(ex)
    else:
        errors['Could not get the TACTIC server'] = ''
    return errors

def removeAssetFromShot(assets, shot):
    assetCount = Counter(assets)
    errors = {}
    if server:
        try:
            sobjects = server.query('vfx/asset_in_shot')
            if sobjects:
                sks = []
                for asset, cnt in assetCount.items():
                    for _ in range(cnt):
                        for sobj in sobjects:
                            if sobj['asset_code'] == asset and sobj[
                                    'shot_code'] == shot:
                                if sobj['__search_key__'] not in sks:
                                    sks.append(sobj['__search_key__'])
                                    break
                if sks:
                    for sk in sks:
                        server.delete_sobject(sk)
            else:
                errors['No Asset found on TACTIC for %s' % shot] = ''
        except Exception as ex:
            errors['Could not delete Assets from %s' % shot] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return errors


def addAssetsToSeq(assets, seq):
    errors = {}
    if server:
        data = [{
            'asset_code': asset,
            'sequence_code': seq
        } for asset in assets]
        try:
            server.insert_multiple('vfx/asset_in_sequence', data)
        except Exception as ex:
            errors['Could not add Assets to TACTIC'] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return errors


def removeAssetsFromSeq(assets, seq):
    assetCount = Counter(assets)
    errors = {}
    if server:
        try:
            sobjects = server.query('vfx/asset_in_sequence')
            if sobjects:
                sks = []
                for asset, cnt in assetCount.items():
                    for _ in range(cnt):
                        for sobj in sobjects:
                            if sobj['asset_code'] == asset and sobj['sequence_code'] == seq:
                                if sobj['__search_key__'] not in sks:
                                    sks.append(sobj['__search_key__'])
                                    break
                if sks:
                    for sk in sks:
                        server.delete_sobject(sk)
            else:
                errors['No Asset found on TACTIC for %s' % seq] = ''
        except Exception as ex:
            errors['Could not delete Assets from %s' % seq] = str(ex)
    else:
        errors['Could not find the TACTIC server'] = ""
    return errors


def getRefsCount():
    refCounts = Counter()
    refs = [
        osp.normcase(osp.normpath(str(x.path))) for x in qutil.getReferences()
    ]
    if refs:
        refCounts.update(refs)
    return refCounts


def getExistingCameraNames():
    names = []
    cams = pc.ls(type='camera')
    for cam in cams:
        names.append(qutil.getNiceName(cam.firstParent().name()))
    return names


def getCameraName():
    return qutil.getNiceName(pc.lookThru(q=True))


def getSelectedAssets():
    geosets = ss_be.findAllConnectedGeosets()
    for _set in geosets:
        yield osp.splitext(
            osp.basename(str(qutil.getRefFromSet(_set).path)))[0].replace(
                '_rig', '').replace('_shaded', '').replace('_model',
                                                           '').replace(
                                                               '_combined', '')


def isSelection():
    return pc.ls(sl=True)


def addCamera(name, start, end):
    cam = qutil.addCamera(name)
    # pc.mel.eval('addInOutAttr;')
    # cam.attr('in').set(start); cam.out.set(end)
    addKeys.add([cam], start, end)
    cam.nearClipPlane.set(1)
    cam.farClipPlane.set(10000000)


def isModified():
    return cmds.file(modified=True, q=True)


def getExt():
    return cmds.file(q=True, type=True)[0]


def checkin(seq, context, desc):
    path = cmds.file(location=True, q=True)
    sk = server.query(
        'vfx/sequence', filters=[('code', seq)])[0]['__search_key__']
    snapshot = server.simple_checkin(
        sk, context=context, file_path=path, mode='copy',
        description=desc)['__file_sobjects__'][0]
    return osp.join(snapshot['checkin_dir'], snapshot['file_name'])


def epCheckin(ep, context, desc):
    path = cmds.file(location=True, q=True)
    sk = server.query(
        'vfx/episode', filters=[('code', ep)])[0]['__search_key__']
    server.simple_checkin(
        sk, context=context, file_path=path, mode='copy', description=desc)


server = None


def getLatestFile(file1, file2):
    latest = file1
    if os.path.getmtime(file2) > os.path.getmtime(file1):
        latest = file2
    return latest


def getAssets(ep, seq, context='shaded/combined'):
    errors = {}
    asset_paths = {}
    asset_count = Counter()
    if ep and seq:
        try:
            maps = symlinks.getSymlinks(
                server.get_base_dirs()['win32_client_repo_dir'])
        except Exception as ex:
            errors['Could not get the maps from TACTIC'] = str(ex)
        if server:
            try:
                asset_codes = [
                    asset['asset_code']
                    for asset in server.query(
                        'vfx/asset_in_sequence',
                        filters=[('sequence_code', seq)],
                        columns=['asset_code'])
                ]
                # asset_codes =
                # server.eval("@GET(vfx/asset_in_sequence['sequence_code',
                # '%s'].asset_code)"%seq)
                asset_codes = list(set(asset_codes))
            except Exception as ex:
                errors['Could not get the Sequence Assets from TACTIC'] = str(ex)
            if not asset_codes: return asset_paths, errors
            # fetch the shots and asset count
            shots, err = getShots(seq)
            if err: errors.update(err)
            if shots:
                shots = shots.keys()
                for shot in shots:
                    shot_assets, err = getAssetsInShot([shot])
                    if err: errors.update(err)
                    if shot_assets: asset_count |= Counter([asset['asset_code'] for asset in shot_assets])
            try:
                ep_assets = server.query(
                    'vfx/asset_in_episode',
                    filters=[('asset_code', asset_codes), ('episode_code',
                                                           ep)])
            except Exception as ex:
                errors['Could not get the Episode Assets from TACTIC'] = str(
                    ex)
            for ep_asset in ep_assets:
                try:
                    snapshot = server.get_snapshot(
                        ep_asset,
                        context=context,
                        version=0,
                        versionless=True,
                        include_paths_dict=True)
                except Exception as ex:
                    errors['Could not get the Snapshot from TACTIC for %s' %
                           ep_asset['asset_code']] = str(ex)
                # if not snapshot: snapshot = server.get_snapshot(ep_asset,
                # context='shaded', version=0, versionless=True,
                # include_paths_dict=True)
                if snapshot:
                    paths = snapshot['__paths_dict__']
                    if paths:
                        newPaths = None
                        if 'maya' in paths:
                            newPaths = paths['maya']
                        elif 'main' in paths:
                            newPaths = paths['main']
                        else:
                            errors[
                                'Could not find a Maya file for %s' % ep_asset[
                                    'asset_code']
                                ] = 'No Maya or Main key found'
                        if newPaths:
                            if len(newPaths) > 1:
                                asset_paths[ep_asset[
                                    'asset_code']] = symlinks.translatePath(
                                        getLatestFile(*newPaths), maps)
                            else:
                                asset_paths[ep_asset[
                                    'asset_code']] = symlinks.translatePath(
                                        newPaths[0], maps)
                        else:
                            asset_paths[ep_asset['asset_code']] = None
                    else:
                        asset_paths[ep_asset['asset_code']] = None
                else:
                    if not asset_paths.has_key(ep_asset['asset_code']):
                        asset_paths[ep_asset['asset_code']] = None
    return asset_paths, asset_count, errors
