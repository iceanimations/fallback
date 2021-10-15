'''
    creates curves between two or more objects
    objects can be curve points and mesh faces
    you can select as many objects as you want

    Author: Qurban Ali (qurban.ali@iceanimations.com)
'''

import pymel.core as pc
from pymel.core import *
from maya.cmds import file
import curve_tool as ct
import maya.mel as mel

def rivet(f, prefix = 'rivet'):
    '''
    @brief: creates Rivet on the Selected Mesh Edges or surface point
    @param rivet: Prefix for the name of rivet ... default='rivet'
    @return: the newly created rivet (locator Transform) object
    '''
    # in case of both mesh edges or surface point we will have a POSI node
    # attached to a parent objec to work with
    Object1 = None
    POSI1 = None
    face = f
    edges = face.getEdges()
    node = face.node()
    listSelected = [str(node.e[edges[0]]), str(node.e[edges[2]])]
    #listSelected = filterExpand(sm=32)
    # @note: if mesh edge was selected
    size = len(listSelected)
    if size > 0:
        if size != 2:
            error('Two Edges Not Selected');
            return

        Object1 = PyNode( listSelected[0].split(u'.')[0] )
        e1 = float( listSelected[0].split(u'[')[1].split(u']')[0] )
        e2 = float( listSelected[1].split(u'[')[1].split(u']')[0] )

        # extract curves from mesh edges and loft them
        CFME1 = createNode('curveFromMeshEdge', n=prefix + 'CurveFromMeshEdge1')
        setAttr('.ihi', 1)
        setAttr ('.ei[0]', e1)
        CFME2 = createNode('curveFromMeshEdge', n=prefix + 'CurveFromMeshEdge2')
        setAttr('.ihi', 1)
        setAttr ('.ei[0]', e2)

        loft1 = createNode('loft', n='rivetLoft1')
        setAttr('.ic', s=2)
        setAttr('.u', True)
        setAttr('.rsn', True)

        POSI1 = createNode('pointOnSurfaceInfo', n=prefix + 'PointOnSurfaceInfo1')
        setAttr('.turnOnPercentage', True)
        # set the POSI on the middle of the lofted plane
        setAttr('.parameterU', 0.5)
        setAttr('.parameterV', 0.5)

        connectAttr( loft1 + '.os', POSI1 + '.is', f=True)
        connectAttr( CFME1 + '.oc', loft1 + '.ic[0]')
        connectAttr( CFME2 + '.oc', loft1 + '.ic[1]')
        connectAttr( Object1 + '.w', CFME1 + '.im')
        connectAttr( Object1 + '.w', CFME2 + '.im')

    # surface point was selected
    else:
        listSelected = filterExpand(sm=41)
        size = len(listSelected)

        if size > 0:
            if size != 1:
                error('One Point Not Selected')
                return

            Object1 = PyNode(listSelected[0].split(u'.')[0])
            u = float( listSelected[0].split(u'[')[1].split(u']')[0] )
            v = float( listSelected[0].split(u'[')[2].split(u']')[0] )

            POSI1 = createNode('pointOnSurfaceInfo',
            n=prefix + 'PointOnSurfaceInfo')
            setAttr('.turnOnPercentage', True)
            setAttr('.parameterU', u)
            setAttr('.parameterU', v)

            connectAttr( Object1 + '.ws', POSI1 + '.is')

        else:
            error ('No Edges or point Selected')
            return

    # creating a locator node as rivet
    loc1 = createNode('transform', n=prefix + '1')
    createNode('locator', n = loc1 + 'Shape', p=loc1)

    # Orienting the rivet locator
    ac1 = createNode('aimConstraint', p=loc1, n=loc1+'_AimConstraint1')
    setAttr('.tg[0].tw', 1)
    setAttr('.a', (0,1,0))
    setAttr('.u', (0,0,1))

    # removing all the transform attributes
    setAttr('.v' , k=False)
    setAttr('.tx', k=False)
    setAttr('.ty', k=False)
    setAttr('.tz', k=False)
    setAttr('.rx', k=False)
    setAttr('.ry', k=False)
    setAttr('.rz', k=False)
    setAttr('.sx', k=False)
    setAttr('.sy', k=False)
    setAttr('.sz', k=False)

    # Connecting all the nodes to make sense
    connectAttr( POSI1 + '.position', loc1 + '.translate')
    connectAttr( POSI1 + '.n', ac1 + '.tg[0].tt')
    connectAttr( POSI1 + '.tv', ac1 + '.wu')
    connectAttr( ac1 + '.crx', loc1 + '.rx')
    connectAttr( ac1 + '.cry', loc1 + '.ry')
    connectAttr( ac1 + '.crz', loc1 + '.rz')

    # selecting and returning the newly created locator
    select(loc1)
    return loc1.getShape() #Object1


def get_curve_point(point):
    '''
    returns the float u value from the nurbsCurveParameter

    @params
    point: nurbsCurveParameter (e.g curve1.u[1.2763633737])
    returns 1.2763633737 (float)
    '''
    return float(point.split('[')[-1].split(']')[0])

def create_curve(objects, CVs, degree, free_curve, free_curve_length, CVs_from_length, CVs_per_unit):
    '''
    This function creates curve between two or more objects
    objects can be mesh faces and curve points (U values)

    @params:
    objects:    list of objects (mesh faces and/or curve points)
    CVs:        no.of control vertices in resulting curve (int)
    degree:     degree of resulting curve (int)
    free_curve: last vertex of resulting curve will be free (bool)
    free_curve_length: length of the tip of the free curve (float)
    CVs_from_length:   calculate the number of CVs in resulting curve from it's length
    CVs_per_unit: Number of CVs (in the resulting curve) per grid unit
    '''
    no_of_objects = len(objects)
    if no_of_objects == 1 and not free_curve:
        pc.error('for one selection, only free curve can be created')
        return
    if not no_of_objects:
        pc.error('No object selected')
        return
    faces = [] #faces in the objects list
    p = [] #float u values on the curves
    points = [] #selected nurbsCurveParameter
    nodes = [] #nodes of selected objects
    newC = [] #list of newly created curves
    locators = [] #list of locators created on the faces
    poci = [] #list pointOnCurveInfo nodes
    indices = [] #indices of faces in the list of selected objects
    sequence_points = [] #sequence of the objects in which the new curve will be created
    strObjects = [str(x) for x in objects] # to fix the pymel bug, covert the faces to string
    # check for the correct selection in the scene
    for obj in objects:
        if type(obj) == pc.general.MeshFace:
           pass
        elif type(obj) == pc.general.NurbsCurveParameter:
             pass
        else:
             pc.error('Selection types are Mesh Faces and Curve Points')
             return
    # seperate the faces and curve points (u values)
    for obj in strObjects:
        if type(pc.PyNode(obj)) == pc.general.MeshFace:
            indices.append(strObjects.index(obj))
            faces.append(pc.PyNode(obj))
    for obj in objects:
        if type(obj) == pc.general.NurbsCurveParameter:
            points.append(obj)
    no_of_points = len(points)
    fc = free_curve
    no_of_CVs = CVs
    no_of_curves = 1 #always creates one curve, otherwise curves are overlaping
    deg = degree

    if deg > 3:
        deg = 3
        pc.warning('New curve is created with degree 3')
    if not CVs_from_length:
        if deg >= no_of_CVs:
            pc.error('Enter the degree atleast 1 less than no. of CVs')
            return
    if deg < 1:
        pc.error('Dgree can not be less than 1')
        return
    # attach the locators on the selected faces
    if faces:
        for face in faces:
            locators.append(rivet(face))
    no_of_locators = len(locators)
    # group the locators under the group "revet_group"
    if locators:
        if pc.objExists('revet_group'):
            pc.parent(locators, 'revet_group')
        else:
            pc.group(locators, n = 'revet_group')
    CVs_to_be_inserted = 0
    if not CVs_from_length:
        CVs_to_be_inserted = no_of_CVs - no_of_points - no_of_locators
    if fc:
        # in free curve mode an extra CV is created, so decrease the CVs by one
        CVs_to_be_inserted = CVs_to_be_inserted - 1
        if CVs_to_be_inserted == -1:
            CVs_to_be_inserted = 0

    if not CVs_from_length:
        if CVs_to_be_inserted < 0:
            pc.delete(locators)
            pc.error('Enter the no. of CVs greater than or eaual to selected CVs/Objects')
            return

    for pnt in points:
        sequence_points.append(pnt)

    # maintain the origunal sequence in which the objects were selected
    i = 0
    for loc in locators:
        sequence_points.insert(indices[i], loc)
        i = i + 1
    total_points = len(sequence_points)
    for i in range(no_of_points):
        poci.append(pc.createNode('pointOnCurveInfo'))

    for pt in points:
        p.append(get_curve_point(pt))
        nodes.append(pt.node())

    # set the parameter attribute of the pointOnCurveInfo nodes
    for j in range(no_of_points):
        poci[j].pr.set(p[j])

    # set the input curves of pointOnCurveInfo nodes
    for k in range(no_of_points):
        nodes[k].worldSpace[0] >> poci[k].ic

    s = None
    for nc in range(no_of_curves):
        s = 0 # index for pointOnCurveInfo node

        if fc:
            # creates an extra CV that is free
            total_points = total_points + 1
        if total_points == degree:
            deg = deg - 1
        if deg > total_points:
            # maximum degree is 3 and no. of minimum objects for curve is 2
            # so maximum times the degree can be greater than objects is 1
            deg = deg - 2
        cu = pc.curve(d = deg,
                    p=[(0,0,0),]*(total_points) )
        newC.append(cu)
        if fc:
            # set the original no. of objects selected
            total_points = total_points - 1
        for l in range(total_points):
            # attaching CVs to pointOnCurveInfo nodes
            if type(sequence_points[l]) == pc.general.NurbsCurveParameter:
                poci[s].p >> newC[nc].cp[l]
                s = s + 1
            else:
                # attaching CVs to the locators
                sequence_points[l].wp >> newC[nc].cp[l]
        if fc:
            # calculate the free CV's position
            pt = pc.dt.Point([0, free_curve_length, 0])
            pma = pc.createNode('plusMinusAverage')
            pma.op.set(2)
            if type(sequence_points[-1]) == pc.general.NurbsCurveParameter:
                poci[-1].p >> pma.i3[0]
            else:
                sequence_points[-1].wp >> pma.i3[0]
            pma.i3[1].set(pt)
            pma.o3 >> newC[nc].cp[total_points]
    # when required no.of CVs is more than the selected objects
    if CVs_from_length:
        curve_length = int(newC[0].length())
        if curve_length < 1:
           curve_length = 1
        CVs_to_be_inserted = (CVs_per_unit*curve_length) - total_points
        # if selected points are more than the newly created curve points
        if CVs_to_be_inserted < 0:
           pc.warning('You selected more objects than the minimum CVs can be created for this length')
    # insert knots into the curve
    if CVs_to_be_inserted > 0:
        newC2 = []
        for cn in range(no_of_curves):
            newC2.append(pc.createNode('nurbsCurve', p = newC[cn]))
            newC[cn].l >> newC2[cn].create
            pc.insertKnotCurve(newC2[cn], ch = True, p = (newC2[cn].minValue.get(), newC2[cn].maxValue.get()), rpo = True,ib = True,
                                          nk = CVs_to_be_inserted)
            newC[cn].getShape().intermediateObject.set(1)
            if fc:
               total_points += 1
            if degree >= total_points + CVs_to_be_inserted:
               de = (total_points + CVs_to_be_inserted) - 1
            else:
                 de = degree
            pc.rebuildCurve(newC2[cn], d = de, kcp = True)
            if fc:
               total_points -= 1
        # group the newly created curves
        if pc.objExists('curves_group'):
            pc.parent(newC2, 'curves_group')
        else:
            pc.group(newC2, n = 'curves_group')

    else:
        # group the newly created curves
        if pc.objExists('curves_group'):
            pc.parent(newC, 'curves_group')
        else:
            pc.group(newC, n = 'curves_group')

    if locators:
       pc.hide(locators)

def gui_handler(points, CVs, degree, free_curve, vicinity, no_of_curves, free_curve_length, CVs_from_length, CVs_per_unit):
    '''
    This function is intermediate between GUI and create_curve fuctions
    accepts inputs from the interface and passes to create_curve function

    @params
    CVs: (intField object) no. of CVs
    degree: (intField object) curve degree
    free_curve: (checkBox object) whether to create a free curve or not
    vicinity: (checkBox object) whether to generate the curves from the
              selected faces
    no_of_curves: (intField object) how many curves from the vicinity
    of the selected objects
    free_curve_length: (floatField object) the length of the tip free curve
    CVs_from_length: (checkBox object) calculate the number of CVs from the length of the newly created curve
    CVs_per_unit: (intField object) CVs per grid unit
    dc: (checkBox Object) whether to create dynamic curves or not
    cons: (checkBox object) whether to create constraints or not
    '''
    neighbours = {} # connected faces of the selected faces
    objs = points
    cv = CVs.getValue()
    d = degree.getValue()
    f = free_curve.getValue()
    v = vicinity.getValue()
    fcl = free_curve_length.getValue()
    n = no_of_curves.getValue()
    CVs_f_l = CVs_from_length.getValue()
    CVs_p_u = CVs_per_unit.getValue()

    create_curve(objs, cv, d, f, fcl, CVs_f_l, CVs_p_u,)
    # when vicinity is on
    if v:
        if n > 1:
            # one curve is already created
            no_of_faces = n - 1
            # set the limit maximum curves can be created
            for obj in objs:
                if type(obj) == pc.general.MeshFace:
                    neighbours[obj] = pc.ls(obj.connectedFaces(), fl = True)
                    l = len(neighbours[obj])
                    if l < no_of_faces:
                        no_of_faces = l
            # call create_curve with the connected faces as first parameter
            # all other parameters remain same
            for i in range(no_of_faces):
                newObjs = []
                for ob in objs:
                    if type(ob) == pc.general.MeshFace:
                        newObjs.append(neighbours[ob][i])
                    else:
                        newObjs.append(ob)
                create_curve(newObjs, cv, d, f, fcl, CVs_f_l, CVs_p_u)

def gui():
    '''
    This function creates a gui
    '''
    #update the database, how many times this app is used
    import site
    site.addsitedir(r'r:/pipe_repo/users/qurban')
    import appUsageApp
    reload(appUsageApp)
    appUsageApp.updateDatabase('curve_tool')
    #////////////////////////////////////////////////////
    points = []
    input_objects = pc.melGlobals.get('$g_curveTool_selList')
    for io in input_objects:
        points.append(pc.PyNode(io))
    no_of_points = len(points)
    if not no_of_points:
        pc.warning('No objects selected')
    with pc.window('Create Curve(s)', wh = (250, 200)) as win:
        with pc.columnLayout():
            pc.text(label = 'Create the curve(s) between two or more objects')
            pc.text('(mesh faces and curve points)')

        with pc.columnLayout():
            with pc.rowColumnLayout( numberOfColumns=1, columnAlign=(1, 'left'), columnAttach=(1, 'left', 0), columnWidth=(1, 258) ):
                pc.separator(style = 'in')
                reSelect = pc.button(label = 'Reselct', w = 258)
                reSelect.setAnnotation('Reselect the objects (mesh faces and curve points)')
                pc.separator(style = 'in')
                reSelect.setCommand(pc.Callback(ct.runSelectionTool, win))
            with pc.rowLayout(numberOfColumns = 3, columnAttach3=('both', 'both', 'both')):
                CVs_from_length = pc.checkBox(label = 'CVs from length')
                pc.text(label = '   CVs per unit:')
                CVs_per_unit = pc.intField(w = 84)
                CVs_per_unit.setValue(2)
                CVs_per_unit.setMinValue(1)
                CVs_from_length.setValue(1)
                CVs_from_length.setAnnotation('Create the number of CVs according to the length of the curve')
                CVs_per_unit.setAnnotation('CVs per grid unit')
            with pc.rowColumnLayout( numberOfColumns=1, columnAlign=(1, 'left'), columnAttach=(1, 'left', 0), columnWidth=(1, 258) ):
                pc.separator(style = 'in')
            with pc.rowLayout(numberOfColumns = 5, columnAttach5=('both', 'both', 'both', 'both', 'both')):
                pc.text(label = 'CVs:')
                CVs = pc.intField(w = 91)
                CVs.setAnnotation('Number of CVs in resulting curve')
                pc.text(label = '   Degree:')
                degree = pc.intField(w = 91)
                degree.setAnnotation('Degree of resulting curve (1 - 3)')
                degree.setMinValue(1)
                degree.setMaxValue(3)
                degree.setValue(3)
                CVs.setMinValue(no_of_points)
                def CVs_from_length_switch(args):
                    if CVs_from_length.getValue():
                        CVs.setEnable(0)
                        CVs_per_unit.setEnable(1)
                    else:
                         CVs_per_unit.setEnable(0)
                         CVs.setEnable(1)
                CVs_from_length_switch(0)
                CVs_from_length.offCommand(CVs_from_length_switch)
                CVs_from_length.onCommand(CVs_from_length_switch)
            with pc.rowColumnLayout( numberOfColumns=1, columnAlign=(1, 'left'), columnAttach=(1, 'left', 0), columnWidth=(1, 258) ):
                pc.separator(style = 'in')
            with pc.rowLayout(numberOfColumns = 3, columnAttach3=('both', 'both', 'both')):
                free_curve = pc.checkBox(label = 'Free Curve')
                free_curve.setAnnotation('Last CV will be free in the space in -y direction')
                pc.text(label = ' curve length:')
                free_curve_length = pc.floatField()
                free_curve_length.setAnnotation('Length from the last selected point in -y dorection')
                free_curve_length.setValue(1.0)
                free_curve_length.setMinValue(0.0)
                def length_switch(args):
                    if not free_curve.getValue():
                        free_curve_length.setEnable(0)
                    else:
                        free_curve_length.setEnable(1)
                length_switch(0)
                free_curve.offCommand(length_switch)
                free_curve.onCommand(length_switch)
            with pc.rowLayout(numberOfColumns = 3, columnAttach3=('both', 'both', 'both')):
                vicinity = pc.checkBox(label = 'Vicinity')
                vicinity.setAnnotation('Generate curve(s) from the vicinity of the selected faces')
                pc.text(label = '      No. of curves:')
                no_of_curves = pc.intField(w = 111)
                no_of_curves.setAnnotation('Total number of curves, you want to create')
                #print no_of_curves.getWidth()
                no_of_curves.setValue(2)
                no_of_curves.setMinValue(1)
                def vicinity_switch(args):
                    if not vicinity.getValue():
                        no_of_curves.setEnable(0)
                    else:
                        no_of_curves.setEnable(1)
                vicinity_switch(0)
                vicinity.offCommand(vicinity_switch)
                vicinity.onCommand(vicinity_switch)
            with pc.rowColumnLayout( numberOfColumns=1, columnAlign=(1, 'left'), columnAttach=(1, 'left', 0), columnWidth=(1, 258) ):
                pc.separator(style = 'in')

            btn = pc.button(label = 'Create', w = 258)
            btn.setAnnotation('Create the curves')
            btn.setCommand(pc.Callback(gui_handler, points, CVs, degree, free_curve, vicinity,
                                                    no_of_curves, free_curve_length, CVs_from_length, CVs_per_unit))
            with pc.rowColumnLayout( numberOfColumns=1, columnAlign=(1, 'left'), columnAttach=(1, 'left', 0), columnWidth=(1, 258) ):
                pc.separator(style = 'in')
    win.setResizeToFitChildren(1)