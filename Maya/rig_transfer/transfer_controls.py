'''
    this module mirrors the controls of a rig
    across a specified axis plan
    geometry of controls should be one of the
    nurbsCircle and nurbsCurve.

    Author: Qurban Ali (qurban.ali@iceanimations.com)
'''

import pymel.all as pm

def mirr_controls(obs, opt):
    '''
        this function mirrors the controls of a rig
        across a specified axis plan

        @params:
            obs: list of objects (nurbsCurves and nurbsCircles)
            opt: axis plan XY, XZ, ZY (string)
    '''
    for ob in obs:
        try:
            vertices = ob.getCVs()
        except AttributeError:
            pm.error('selection is not NURBS Circle or Curve')
            return
        # set the object pivot at the center
        pm.xform(ob, cp = True)
        dupe = pm.duplicate(ob, rr=True)[0]
        # get transform position of the object
        pos = pm.xform(ob, q=True, ws=True, t=True)
        if opt=='YZ':
            pos[0] *= -1
            dupe.sx.set(-1)
            # control points of the object
            points = [ (pm.dt.Point(-x.x, x.y, x.z) ) for x in ob.getCVs(space='world')]
        if opt=='XZ':
            pos[1] *= -1
            dupe.sy.set(-1)
            points = [ (pm.dt.Point(x.x, -x.y, x.z) ) for x in ob.getCVs(space='world')]
        if opt=='XY':
            pos[2] *= -1
            dupe.sz.set(-1)
            points = [ (pm.dt.Point(x.x, x.y, -x.z) ) for x in ob.getCVs(space='world')]
        # set the position of the duplicate transform
        pm.xform(dupe, ws=True, t=pos)
        dupe.setCVs(points, space='world')
        # freez transform
        pm.makeIdentity(dupe, apply=True, t=1, r=1, s=1, n=0)
        grp = pm.group(dupe, name='mirr_'+ob.name())
        pm.xform(grp, cp=True)
        # rotate the group transform to set the inverse rotation
        # in the duplicate transform
        if opt == 'YZ':
            grp.ry.set(grp.ry.get()+180)
            grp.rz.set(grp.rz.get()+180)
        if opt == 'XZ':
            grp.rx.set(grp.rx.get()+180)
            grp.rz.set(grp.rz.get()+180)
        if opt=='XY':
            grp.rx.set(grp.rx.get()+180)
            grp.ry.set(grp.ry.get()+180)

        # scale the duplicate transform to get the actual mirror
        if opt=='YZ':
            dupe.rx.set(dupe.rx.get()+180)
        if opt=='XZ':
            dupe.ry.set(dupe.ry.get()+180)
        if opt=='XY':
            dupe.rz.set(dupe.rz.get()+180)
        pm.makeIdentity(dupe, apply=True, t=1, r=1, s=1, n=0)
        #pm.makeIdentity(grp, apply=True, t=1, r=1, s=1, n=0)
        pm.xform(dupe, cp = True)

def gui_handler(mirror_plan):
    '''
        this function handles the out from gui()
        and passes those outputs to mirr_controls()
        as an input

        @param:
            mirror_plane: mirror axis plan (radioControl object)
    '''
    obs = pm.ls(sl=True)
    # get the name of selected radio button
    axis = mirror_plan.getSelect()
    # get the string name of the selected radio button
    opt = pm.uitypes.RadioButton(axis).getLabel()
    mirr_controls(obs, opt)

def gui():
    '''
        creates a gui
    '''
    # update the database, how many times this app is used
    import site
    site.addsitedir(r'r:/pipe_repo/users/qurban')
    import appUsageApp
    reload(appUsageApp)
    appUsageApp.updateDatabase('rigTransfer')
    #/////////////////////////////////////////////////////
    with pm.window('Mirror Controls') as win:
        with pm.columnLayout():
            with pm.rowLayout(numberOfColumns=4, columnAttach4=('both', 'both', 'both', 'both')):
                pm.text(label='Mirror Plan:       ')
                mirror_plan = pm.radioCollection()
                x = pm.radioButton(label='XY')
                y = pm.radioButton(label='YZ')
                z = pm.radioButton(label='XZ')
            btn = pm.button(label='Mirror', w=210)
            btn.setCommand(pm.Callback(gui_handler, mirror_plan))

def main():
    gui()

if __name__ == '__main__':
    main()