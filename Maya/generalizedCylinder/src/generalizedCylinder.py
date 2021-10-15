'''
:file: generalizedCylinder.py

* TODO: speedup UV adjustment

'''
__all__ = ['generalizedCylinder']

import pymel.core as pc
import re
_pattern = re.compile(r'(.*?)(\d+)$')

from curveControlLocs import addCurveControlLocs


def getContainingEdges(faces):
    ''' Given the faces of a mesh get all the surrounding Edges
    :type Mesh: pymel.core.nt.Mesh()
    :rtype: list of strings of pymel.MeshEdge()
    '''
    return pc.polyListComponentConversion(faces, ff=1, te=1, bo=1)


def expandUV(faces):
    ''' Given the mesh and faces Expand the v-range to [0,1]
    :type mesh: pymel.core.nt.Mesh()
    :type faces: list of pymel.MeshFace()
    '''
    maps = [pc.MeshUV(m) for m in pc.polyListComponentConversion(faces, ff=1,
        tuv=1)]
    uv_ids = []
    for m in maps:
        uv_ids.extend(m.indices())
    meshShape = pc.nt.Mesh( pc.polyListComponentConversion(faces)[0] )
    sorted_ids = sorted(uv_ids, key=lambda x:meshShape.getUV(x)[1])
    low, hi = sorted_ids[:len(sorted_ids)/2], sorted_ids[len(sorted_ids)/2:]
    pc.polyEditUV([meshShape.map[l] for l in low], v=0, r=False)
    pc.polyEditUV([meshShape.map[h] for h in hi], v=1, r=False)


def expandAllUV(faces):
    ''' Given the faces of return UVs in two separate lists of hi and low and
    then map low to v=0, hi to v=1 '''
    hi = []
    low = []
    meshShape = pc.nt.Mesh( pc.polyListComponentConversion(faces[0])[0] )
    for f in faces:
        maps = [pc.MeshUV(m) for m in pc.polyListComponentConversion(f,
            ff=1, tuv=1)]
        uv_ids = []
        for m in maps:
            uv_ids.extend(m.indices())
        sorted_ids = sorted(uv_ids, key = lambda x:meshShape.getUV(x)[1])
        half = len(sorted_ids)/2
        low.extend(sorted_ids[:half])
        hi.extend(sorted_ids[half:])
    pc.polyEditUV([meshShape.map[l] for l in low ], v=0, r=False)
    pc.polyEditUV([meshShape.map[h] for h in hi  ], v=1, r=False)


def adjustCylinderUVs(mesh, uvset="map1", tubeSections=4, startIndex=0,
        endIndex=0):
    ''' Given a generalized cylinder as ``mesh`` adjust its UVS by
    splitting for each tube sub-segment and placing within

    :type mesh: pymel.core.nt.Transform()
    :type uvset: str
    :type tubeSections: int
    :type startIndex: int
    :type endIndex: int
    '''
    meshShape = pc.nt.Mesh(mesh.getShape(type='mesh'))
    if uvset not in meshShape.getUVSetNames():
        uvset = meshShape.getUVSetNames()[0]
    meshShape.setCurrentUVSetName(uvset)
    nf = meshShape.numFaces()
    edges = []
    faces = []
    for vt in range(startIndex, nf-endIndex, tubeSections):
        faces.append(meshShape.f[vt:vt+tubeSections-1])
        #edges.extend(getContainingEdges(faces[-1]))
    edges = [meshShape.e[0:tubeSections]]
    for i in range(tubeSections):
        edges.append(meshShape.e[tubeSections+i::tubeSections*2])
    pc.polyMapCut(edges)
    expandAllUV(faces)


def generalizedCylinder(curve, name="generalizedCylinder1", parent='|',
        addControls=False, samplesPerLength=2,
        tubeSections=4, twistRate=0.5, brushWidth=0.5, rebuildSpansMult = 4,
        adjustUVs=True, closeEnds=True, dispCV=False):
    ''' Generate paintEffects Cylinder over ``curve``

    :type curve: pymel.core.nt.NurbsCurve()
    :type samplesPerLength: float
    :type tubeSections: int
    :type twistRate: float
    :type brushWidth: float
    :rtype: (pymel.core.nt.Mesh(), pymel.core.nt.Stroke())
    '''
    # create the main transform
    mesh = pc.createNode('transform', n=name, parent=parent)
    match = _pattern.match(str(mesh))
    if not match:
        num = ""
        name = name.split("|")[-1]
    else:
        name = match.group(1).split("|")[-1]
        num = match.group(2)

    if addControls:
        _, curve = addCurveControlLocs(curve)

    # create stroke
    strokeShape = pc.createNode('stroke', n=name+'StrokeShape'+str(num), p=mesh)
    strokeShape.pathCurve[0].samples.set(round(samplesPerLength*curve.length()))
    strokeShape.drawAsMesh.set(True)
    strokeShape.displayPercent.set(100)
    strokeShape.meshQuadOutput.set(True)
    strokeShape.minimalTwist.set(True)
    strokeShape.v.set(False)
    strokeShape.io.set(True)

    # create brush
    brush = pc.createNode('brush', n=name+'Brush'+str(num))
    brush.tubeSections.set(tubeSections)
    brush.twistRate.set(twistRate)
    brush.brushWidth.set(brushWidth)
    mesh.addAttr("width", at="float", dv=brushWidth, k=True)
    mesh.addAttr("twistRate", at="float", dv=twistRate, k=True)

    # create final mesh
    meshShape = pc.createNode('mesh', n=name+'Shape'+str(num), p=mesh)

    rebuildCurve = pc.createNode('rebuildCurve', n=name+'RebuildCurve'+str(num))
    rebuildCurve.rt.set(0)
    rebuildCurve.end.set(1)
    rebuildCurve.kr.set(1)
    rebuildCurve.kcp.set(0)
    rebuildCurve.kep.set(1)
    rebuildCurve.kt.set(0)
    rebuildCurve.s.set(curve.spans.get() * rebuildSpansMult)
    rebuildCurve.d.set(3)
    rebuildCurve.tol.set(0.01)

    # make the connections
    curve.dispCV.set(dispCV)
    curve.worldSpace[curve.instanceNumber()] >> rebuildCurve.ic
    rebuildCurve.oc >> strokeShape.pathCurve[0].curve
    mesh.width >> brush.brushWidth
    mesh.twistRate >> brush.twistRate
    brush.outBrush >> strokeShape.brush
    strokeShape.outMainMesh >> meshShape.inMesh

    # adjust UVs and assign default shader
    if adjustUVs:
        adjustCylinderUVs(mesh, tubeSections=tubeSections)

    pc.sets("initialShadingGroup", e=1, forceElement=meshShape)

    # close the ends of the cylinder
    if closeEnds:
        pc.polyCloseBorder(mesh, ch=1);
        tf = mesh.numFaces()
        startFace, endFace = mesh.f[tf-1], mesh.f[tf-2]
        pc.polyExtrudeFacet(endFace, constructionHistory=1,
                keepFacesTogether=1, divisions=2, twist=0, taper=1, off=0,
                thickness=0, smoothingAngle=30);
        pc.polyExtrudeFacet(startFace, constructionHistory=1,
                keepFacesTogether=1, divisions=2, twist=0, taper=1, off=0,
                thickness=0, smoothingAngle=30);

    pc.select(mesh, r=True)
    return mesh


def _main_():
    for i in pc.ls(type='nurbsCurve'):
        generalizedCylinder(i, tubeSections=8, adjustUVs=True, closeEnds=False,
                dispCV=True)


if __name__ == '__main__':
    import cProfile
    cProfile.run('_main_()')
