import pymel.core as pc


__all__ = ['addCurveControlLocs']


def addCurveControlLocs(curveShape1):
    """Add curve Control locators to that curvy (or straight) thing
    :type curveShape1: pymel.core.nt.NurbsCurve()
    """
    curve1 = curveShape1.getParent()
    if not pc.attributeQuery('controlLocatorScale', n=curve1, exists=True):
        curve1.addAttr( 'controlLocatorScale', at='float', dv=1, k=0 )

    # convert curve to d=1
    rc0 = pc.createNode( 'rebuildCurve' )
    rc0.d.set( 1 )
    rc0.kcp.set( True )
    rc0.rt.set( 0 )
    minValue, maxValue = curveShape1.minMaxValue.get()
    spans = curveShape1.spans.get()
    spans = spans if spans else 1.0
    uStep = ( maxValue-minValue ) / spans
    oldName = curveShape1.split( '|' )[-1]
    instNo = curveShape1.instanceNumber()

    # create history
    lsm = pc.createNode( 'leastSquaresModifier' )
    curveShape1.rename( oldName + 'Orig' )
    curveShape1.io.set( True )
    oldShape = curveShape1
    curveShape1 = pc.createNode( 'nurbsCurve', p=curve1, n=oldName )

    locators = []
    uVal = minValue
    # add and connect all control locs
    for icv in range( oldShape.numCVs() ):
        newLocator = pc.spaceLocator(
                p=oldShape.cv[icv].getPosition(space='world') )
        newLocator.setParent( curve1 )
        pc.makeIdentity( newLocator, apply=True, t=1, r=1, s=1, n=0 )
        locators.append( newLocator )
        newLocator.setPivots( newLocator.worldPosition[0].get(),
                worldSpace=True )
        lsm.pointConstraint[icv].puv.pcu.set( uVal )
        lsm.pointConstraint[icv].pw.set( 1.0 )
        newLocator.worldPosition[0] >> lsm.pointConstraint[icv].pointPositionXYZ
        curve1.controlLocatorScale >> newLocator.localScaleX
        curve1.controlLocatorScale >> newLocator.localScaleY
        curve1.controlLocatorScale >> newLocator.localScaleZ
        uVal += uStep

    # rebuild to convert back to d=3
    rc1 = pc.createNode( 'rebuildCurve' )
    rc1.d.set( 3 )
    rc1.end.set( 1 )
    rc1.kcp.set( True )
    rc1.kep.set( False )
    rc1.kr.set( 1 )

    rc2 = pc.createNode( 'rebuildCurve' )
    rc2.rt.set( 4 )
    rc2.d.set( 3 )
    rc2.tol.set( 0.001 )
    rc2.end.set( 1 )
    rc2.kr.set( 1 )

    # make the final connections
    rc1.oc >> rc2.ic
    lsm.outputNurbsObject >> rc1.ic
    rc0.oc >> lsm.inputNurbsObject
    oldShape.worldSpace[instNo] >> rc0.ic
    oldShape.worldMatrix[instNo] >> lsm.wto
    rc2.oc >> curveShape1.create

    return curve1, curveShape1


def main():
    """@todo: Docstring for main.
    :returns: @todo
    """
    print addCurveControlLocs( pc.SCENE.curveShape1 )


if __name__ == '__main__':
    main()
