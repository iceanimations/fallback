'''
   changes the mouse pointer to curve point and mesh face selection tool
   stores the selected points or mesh faces

   Author: Talha Ahmad
'''



import pymel.core as pc

def runSelectionTool(win):
    if win:
        win.delete()
    tool= pc.scriptCtx(
           title="curve tool",
           toolCursorType="edit",
           totalSelectionSets=1,
           cumulativeLists=False,
           expandSelectionList=True,
           ts="global int $g_curveTool_toolFinished; $g_curveTool_toolFinished=0;",
           fcs=("global string $g_curveTool_selList[];\n" +
                  "global int $g_curveTool_numToDo;" +
                  "global string $g_curveTool_tool;" +
                  "global int $g_curveTool_toolFinished; $g_curveTool_toolFinished=1;" +
                  "$g_curveTool_selList = stringArrayCatenate($g_curveTool_selList, $Selection1);\n" +
                  "$g_curveTool_numToDo = $g_curveTool_numToDo - 1;\n" +
                  "if ( $g_curveTool_numToDo > 0 ) { select -cl; evalDeferred(\"setToolTo $g_curveTool_tool\"); \n" +
                  "print (\"\\nselect \" + $g_curveTool_numToDo + \" more things \\n\"); }\n"),
            tf=("global int $g_curveTool_toolFinished;\nglobal int $g_curveTool_numToDo; \n" +
                "if ($g_curveTool_toolFinished == 0 || $g_curveTool_numToDo <= 0) python(\"import plugins.curve_tools.create_curve;reload(plugins.curve_tools.create_curve);plugins.curve_tools.create_curve.gui()\");" ),

           setNoSelectionPrompt="Select a face or a curvePoint or press Q to exit",
           setNoSelectionHeadsUp="Select a face or a curvePoint or press Q to exit",
           setAutoToggleSelection=False,
           setAutoComplete=True,
           setSelectionCount=True,
           cpp=True,
           fc=True )

    pc.select(cl=True)
    pc.melGlobals.initVar( 'string[]', '$g_curveTool_selList' )
    pc.melGlobals['$g_curveTool_selList'] = []
    pc.melGlobals.initVar( 'int', '$g_curveTool_numToDo' )
    pc.melGlobals['$g_curveTool_numToDo'] = 10
    pc.melGlobals.initVar( 'string', '$g_curveTool_tool' )
    pc.melGlobals['g_curveTool_tool'] = tool
    pc.setToolTo(tool)