import site, sys, os
op = os.path
DIR = op.dirname(__file__)
MEL = op.join(DIR, 'mel')
LIBMEL = op.join(DIR, 'libmel')
XPM = op.join(DIR, 'xpm')
import os
os.environ['XBMLANGPATH'] = XPM + ';' + os.environ.get('XBMLANGPATH', '')

winCache = []

# Layout #######################################################

def _createLayout(*args):
    if __tacticLogin():
        import createLayout
        reload(createLayout)
        createLayout.Window().show()
        
def exportSnap(*args):
    import exportSnapshots
    reload(exportSnapshots)
    exportSnapshots.Window().show()

# General ######################################################

def repPro(*args):
    if __tacticLogin():
        import replaceProxies
        replaceProxies.replace()

def duplicatePF(*args):
    import duplicatePerFrame
    reload(duplicatePerFrame)
    duplicatePerFrame.Window().show()

def Asset_Manager(*args):
    import maya.cmds as mc
    site.addsitedir(r"R:\Pipe_Repo\Projects\DAM\bin")

    if "2013" in mc.about(v=1):
        site.addsitedir(r"R:\Pipe_Repo\Projects\DAM\bin\external\maya2013")
    else:
        site.addsitedir(r"R:\Pipe_Repo\Projects\DAM\bin\external\maya2011")

    import dam
    dam.main()

def deleteAllKeys(*args):
    import pymel.core as pc
    for node in pc.ls(type='animCurve'):
        try:
            pc.delete(node)
        except:
            pc.warning('Cannot delete node %r'%node)

def bundleScene(*args):
    import sceneBundle as sb
    reload(sb)
    sb.Window().show()

def Save_Increment(*args):
    site.addsitedir(r"R:\Python_Scripts\plugins\incrementSave\src")
    import logic
    reload(logic)
    logic.saveFile()

def Select_By_Angle(*args):
    import imp
    select = imp.load_source("angleSelect", r"r:/Pipe_Repo/Users/Hussain/scripts/fx_growSelectionByEdgeAngle.py")
    select.run()

def removeNamespace(*args):
    import removenamespace as rn
    reload(rn)
    rn.Remover().show()

def nameMtl(*args):
    import namemtl
    reload(namemtl)
    namemtl.Window().show()

# Dynamics #####################################################

def BakeInstancer(*args):
    import bakeInstancer as bi
    reload(bi)
    bi.Window().show()

def Instance_To_Geometry(*args):
    import imp
    select = imp.load_source("instancer", r"R:\Pipe_Repo\Users\Hussain\scripts\sag_instancerToGeometry.py")
    select.run()

# Look Development #####################################################

def addAttrNanoScreen(*args):
    from .python import nanoScreenMark
    reload(nanoScreenMark)
    nanoScreenMark.addAttrToFileNode()

def postfixHier(*args):
    import postfixHierarchy
    reload(postfixHierarchy)
    postfixHierarchy.Window()

# Lighting #####################################################

def launchLightFlicker(*args):
    import lightFlicker
    reload(lightFlicker)
    lightFlicker.addFlicker()

def _proxyCacheSwitch(*args):
    import proxyCacheSwitch
    reload(proxyCacheSwitch)
    proxyCacheSwitch.Window().show()

def fillinout_RO(*args):
    import fillinoutRO
    reload(fillinoutRO)
    fillinoutRO.fill()

def _setupMasterScene(*args):
    import setupMasterScene as sms
    reload(sms)
    sms.Window().show()

def _createShots(*args):
    import createShots
    reload(createShots)
    createShots.Window().show()

def fixRSTextures(*args):
    import ICEScriptNode as sb
    reload(sb)
    sb.addNode()

def enable_aov_redshift(*args):
    import redshift_aov_enable
    reload(redshift_aov_enable)
    redshift_aov_enable.Window().show()

def toRedshift(*args):
    import arnoldToRedshift as ars
    reload(ars)
    ars.Window().show()

def texturesReloader(*args):

    import textureReloader as tr
    reload(tr)
    tr.Window().show()

def ShaderTransfer(*args):
    import shaderTransfer
    reload(shaderTransfer)
    shaderTransfer.Window().show()

def SceneCheck(*args):

    site.addsitedir(r"R:\Python_Scripts\plugins\sceneCheck_v1.0.0")
    import runSceneCheck
    reload(runSceneCheck)
    
def RedshiftAOVTools(*args):
    from .python import RedshiftAOVTools
    reload(RedshiftAOVTools)
    return RedshiftAOVTools.rsAOVToolShow()

# Animations ###################################################
    
def selectMarker(*args):
    import markerSelect
    reload(markerSelect)
    markerSelect.Window().show()

def launchMSE(*args):
    if __tacticLogin():
        import multiShotExport as mse
        reload(mse)
        mse.Window().show()

def _addKeyFrame(*args):
    import addKeys
    reload(addKeys)
    addKeys.add()

def setupHIK(*args):
    import setupHumanIK
    reload(setupHumanIK)
    setupHumanIK.setup()

def zvParentMaster(*args):
    import ZvP.ZvParentMaster as zvp
    reload(zvp)
    zvp.ZvParentMaster()

def animTexture(*args):

    from .python.animTexture import animTexture
    return animTexture()

def displayRenderLayersInfo(*args):
    import renderLayerInfo
    reload(renderLayerInfo)
    renderLayerInfo.Window().show()

def EnlargeHUDFonts(*args):
    '''
		||Script to enlarge Heads Up Display Text.||
		============================================


    Copy and paste the following Python script in your "PYTHON" Script Editor,
    and run it.
    '''
    import pymel.core as pc

    pc.headsUpDisplay("HUDCurrentFrame", dfs = "large", e=True, lfs = "large", bs = "large")
    pc.headsUpDisplay("HUDCameraNames", e=True, dfs = "large" ,lfs = "large", bs = "large")

def CacheImportExport(*args):
    import CacheImportExport as cie
    reload(cie)
    cie.Window().show()

def Fill_In_Out(*args):
    import fillinout
    reload(fillinout)
    fillinout.fill()

def submit_shot(*args):
    import multishot
    reload(multishot)
    multishot.Window().show()
    
# Rigging #######################################################

def connectObjects(*args):
    import objectsConnect
    reload(objectsConnect)
    objectsConnect.Window().show()

def rig_renamer(*args):
    import rigrenamer
    rigrenamer.gui()

# Rendering ####################################################

def matte_ids(*args):
    import matteIds
    reload(matteIds)
    matteIds.Window().show()

def _renderShots(*args):
    import renderShots
    reload(renderShots)
    renderShots.Window().show()

def addMtlIds(*args):
    import addMaterialIds
    reload(addMaterialIds)
    addMaterialIds.Window().show()

def addObjectIds_auto(*args):
    import addIds_auto
    reload(addIds_auto)
    addIds_auto.Window().show()

def addObjectIds(*args):
    import addIds
    reload(addIds)
    addIds.Window().show()

def setupContLayer(*args):
    import setupContactLayer
    reload(setupContactLayer)
    setupContactLayer.Window().show()

def setupScene(*args):
    import setupSaveScene
    reload(setupSaveScene)
    setupSaveScene.setupScene()
    
def setupSGNodes(*args):
    import rsRenderIssues
    reload(rsRenderIssues)
    rsRenderIssues.add()

def setupPasses(*args):
    import AOVRenderPanel
    reload(AOVRenderPanel)

def slicedRender(*args):
    import AiBatchRender as br
    reload(br)
    br.Window().show()

# Modeling #####################################################

def Create_Rope(*args):
    import generalizedCylinder as gc
    reload(gc)
    win = gc.interface2.Window()
    win.show()

def Generalized_Cylinder(*args):
    import generalizedCylinder as gc
    reload(gc)
    win = gc.interface.Window()
    win.show()

def snapVertexToMiddleTool(*args):
    ''' Define tools to select two sets of vertices '''
    """
    File: snapVertexToMiddleTool.py
    Author: Talha Ahmed
    Email: talha.ahmed@gmail.com
    Github: github.com/talha81
    Description: Describes a tool chain for Autodesk Maya to select two sets of
    vertices, whereupon the second set of vertices are transformed to the mid point
    of the first set of vertices. This simple tool can seldom be of use in modeling
    and rigging. Works in Maya 2011. Code can be made shorter in Maya2013 with the
    'remember selection order' feature switched on

    snapVertexToMiddleTool.py
    Copyright (C) 2013 ICE Animations (Pvt.) Ltd.

    This library is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this library; if not, see <http://www.gnu.org/licenses/>.
    """

    def snapVertexToMiddle(outerVertices=[], innerVertices=[]):
        ''' Snap all 'innerVertices' to the mid point of all the outerVertices
        '''
        import maya.cmds as mc
        import maya.mel as mm

        if not outerVertices or len(outerVertices) < 2:
            mc.error("Please provide at least 2 outer vertices")
        if not outerVertices or len(outerVertices) < 1:
            mc.error("Please provide at least 1 inner vertices")
        ends = outerVertices
        sumPos = [ 0, 0, 0 ]
        for ov in ends:
            sumPos = [ sumPos[i]+p
                    for i,p in enumerate(mc.pointPosition( ov, w=True)) ]
        sumPos = [x/len(ends) for x in sumPos]
        for iv in innerVertices:
            mc.move(sumPos[0], sumPos[1], sumPos[2], iv, ws=True, a=True)

    def snapVertexToMiddleToolHandler():
        ''' gets called when the tool is finished '''
        done = mm.eval("$g_svtmt_tool_done_py = $g_svtmt_tool_done")
        if done == 1.0:
            selov = mm.eval("$g_svtmt_ov_selection_py = $g_svtmt_ov_selection")
            seliv = mm.eval("$g_svtmt_iv_selection_py = $g_svtmt_iv_selection")
            snapVertexToMiddle(selov, seliv)

    mc.select(cl=1)

    # last tool in the chain - to select the inner vertices
    ivctx = mc.scriptCtx(title="SnapVertexTool(InnerVertex)",
            toolCursorType="edit",
            totalSelectionSets=1,
            cumulativeLists=False,
            showManipulators=True,
            expandSelectionList=True,
            euc=True,
            setNoSelectionPrompt="Select atleast one vertex for snapping",
            setNoSelectionHeadsUp="Select atleast one vertex for snapping",
            setDoneSelectionPrompt="Hit Enter to Transform Selected Vertex",
            setAutoToggleSelection=True,
            setAutoComplete=False,
            polymeshVertex=True,
            setSelectionCount=1,
            setAllowExcessCount=True,
            ts=("select -cl; global string $g_svtmt_iv_selection[];\n"+
                    "global float $g_svtmt_tool_done;\n"+
                    "$g_svtmt_tool_done=0.75;\n"+
                    "$g_svtmt_iv_selection={};\n"),
            fcs=("global string $g_svtmt_iv_selection[];\n"+
                    "$g_svtmt_iv_selection = $Selection1;\n"+
                    "global float $g_svtmt_tool_done;\n"+
                    # mark selection as complete
                    "$g_svtmt_tool_done=1.0;\n"+
                    # Calling the tool handler function
                    ('python("' + snapVertexToMiddleToolHandler.__name__ + '()");'))
            )

    # tool to select the outer vertices
    ovctx = mc.scriptCtx(title="SnapVertexTool(OuterVertices)",
            toolCursorType="edit",
            totalSelectionSets=1,
            cumulativeLists=False,
            showManipulators=True,
            expandSelectionList=True,
            euc=True,
            setNoSelectionPrompt="Select atleast two outer vertices",
            setSelectionPrompt="Select more outer vertices or Hit Enter ",
            setSelectionHeadsUp="Select more outer vertices or Hit Enter ",
            setDoneSelectionPrompt="Select more outer vertices or Hit Enter ",
            setNoSelectionHeadsUp="Select atleast two outer vertices",
            setAutoToggleSelection=True,
            setAutoComplete=False,
            polymeshVertex=True,
            setSelectionCount = 2,
            setAllowExcessCount = True,
            ts=('global string $g_svtmt_ov_selection[];\n' +
                    "global float $g_svtmt_tool_done;\n"+
                    "$g_svtmt_tool_done=0.25;\n"+
                    '$g_svtmt_ov_selection = {};\n'),
            fcs=('global string $g_svtmt_ov_selection[];\n' +
                    "global float $g_svtmt_tool_done;\n"+
                    "$g_svtmt_tool_done=0.5;\n"+
                    'global string $g_svtmt_tool;\n'+
                    '$g_svtmt_ov_selection = $Selection1;\n' +
                    # calling the next tool in the chain
                    'evalDeferred("setToolTo " + $g_svtmt_tool + ";")') )

    mc.select(cl=1)
    #preparing global variables for the tools
    mm.eval( "global string $g_svtmt_ov_selection[];" +
                    "$g_svtmt_ov_selection={};" )
    mm.eval( "global string $g_svtmt_iv_selection[];" +
                    "$g_svtmt_iv_selection={};" )
    mm.eval( "global float $g_svtmt_tool_done;\n"+
                    "$g_svtmt_tool_done=0.0;\n")
    mm.eval( 'global string $g_svtmt_tool;\n'+
                    '$g_svtmt_tool="%s";\n' % ivctx)
    mc.setToolTo ( ovctx )

def sag(*args):
    import sag
    reload(sag)
    sag.assign()

# TACTIC #######################################################

def _addAssets(*args):
    if __tacticLogin():
        import addAssets
        reload(addAssets)
        addAssets.Window().show()
    
def __tacticLogin():
    # get the user
    import login
    reload(login)
    import auth.user as user

    if not user.user_registered():
        if not login.Dialog().exec_():
            return
    return True

def __explorer():
    if __tacticLogin():
        import checkoutin
        reload(checkoutin)
        return checkoutin

def showMainBrowser(*args):
    checkoutin = __explorer()
    if checkoutin:
        win = checkoutin.MainBrowser()
        win.show()

def ShotExplorer(*args):
    checkoutin = __explorer()
    if checkoutin:
        win = checkoutin.ShotExplorer()
        win.show()

def showPublishedAssets(*args):
    checkoutin = __explorer()
    if checkoutin:
        checkoutin.pr.run_in_maya()

def Logout(*args):
    import pymel.core as pc
    import auth.user as user
    if user.user_registered():
        user.logout()
        pc.warning("You are now logged out from TACTIC")
    else: pc.warning("You are not logged in...")

def MyTasks(*args):
    checkoutin = __explorer()
    if checkoutin:
        win = checkoutin.MyTasks()
        win.show()

def SceneBreakdown(*args):
    # get the user
    import login
    import auth.user as user

    if not user.user_registered():
        if not login.Dialog().exec_():
            return

    import breakdown
    reload(breakdown)
    win =  breakdown.Breakdown()
    win.show()
    
def published_assets(*args):
    pass

# Utilities ####################################################

def installSundayPipeline(*args):
    from .python import installSundayPipeline as ispp
    ispp.install()

def RandomSelection(*args):
    import randomselection as rs
    reload(rs)
    rs.Window().show()

def makeTearableShelf(*args):
    import pymel.core as pc
    mainShelfLayout = pc.ui.PyUI('ShelfLayout')
    allShelves = mainShelfLayout.getChildren()

    ts = pc.tabLayout(mainShelfLayout, q=1, st=1)
    for i in allShelves:
        pc.tabLayout(mainShelfLayout, e=1, st=i)
    pc.tabLayout(mainShelfLayout, e=1, st=ts)


    if pc.window('TearableShelfWindow', exists = True):
        pc.deleteUI('TearableShelfWindow', window=True)

    if pc.dockControl('TearableShelf', exists=True):
        pc.deleteUI('TearableShelf', ctl=True)

    win = pc.window('TearableShelfWindow')
    with pc.frameLayout(l='', parent=win):
        with pc.tabLayout():
                for s in allShelves:
                    shelfButtons = pc.shelfLayout(str(s), q=1, ca=1)
                    with pc.rowColumnLayout(s.split('|')[-1], nc=5) as rc:
                        print 'Creating Tearable Shelf Tab', s.split('|')[-1]
                        if shelfButtons:
                            for sb in shelfButtons:
                                sb = pc.ui.PyUI(sb)
                                com = sb.getCommand()
                                def command(com):
                                    exec(com)
                                if sb.getSourceType() == 'mel':
                                    command = lambda com: pc.Mel.eval(com)
                                pc.symbolButton(i=sb.getImage(),
                                        c=pc.Callback(command, com),
                                        annotation = sb.getAnnotation(),
                                        w=sb.getWidth(),
                                        h=sb.getHeight() )
        pc.dockControl('TearableShelf', area="right", content=win,
                allowedArea = ["left", "right", "top", "bottom"],
                l='Tearable Shelf')

def tearableShelf(*args):
    makeTearableShelf()

def enableMultiStereoCam(*args):
    import mvstereo
    reload(mvstereo)
    mvstereo.registerMultiRig()

def callStudioLibrary(*args):
    import studiolibrary
    studiolibrary.main()


def substanceImporterApplyToSelected(*args):
    import SubstanceImporter
    SubstanceImporter.apply_to_selected()


# MEL ##########################################################
for item in os.listdir(LIBMEL):
    import pymel.core as pc
    entry = op.join(MEL, item)
    try:
        pc.mel.eval('source "%s"' %(entry.replace('\\', '/')))
    except BaseException as be:
        pc.warning('Error sourcing %s: %s' %(entry, str(be)))

for item in os.listdir(MEL):
    entry = op.join(MEL, item)

    if (op.isfile(entry) and entry.endswith('.mel')
        and '.' not in item[:item.find('.mel')]):
        def create_foo(item = item):
            def foo(*args, **kwargs):
                import pymel.core as pc
                entry = op.join(MEL, item)
                pc.mel.eval('source "%s"' %(entry.replace('\\', '/')))
                pc.mel.eval(item[:item.find('.mel')] + "();")
            return foo

        foo = create_foo(item)
        setattr(sys.modules[__name__], item[:item.find('.mel')], foo)
        del foo

#def addCameraInfoHUD(*args):
    #import pymel.core as pc

__all__ = ['Menu']

class Menu():

    @classmethod
    def call(self, *args, **kwargs):
        return getattr(sys.modules[__name__], kwargs['call'])

    @classmethod
    def help(self):
        pass
