# pieces of code picked up from
# http://therenderblog.com/loading-render-passesaovs-inside-maya-renderview-with-python/

import os
import pymel.core as pc
import maya.cmds as cmds
op = os.path

switchScript = '''
global proc string[] rsGetRenderViewLastRenderInfo() {
    string $editor[] = `getPanel -sty renderWindowPanel`;
    string $renderViewPCA = `renderWindowEditor -q -pca $editor[0]`;
    string $buffer[];
    tokenize $renderViewPCA "\\n" $buffer;
    tokenize $buffer[1] " " $buffer;
    string $renderViewLastRenderCamera = "";
    string $renderViewLastRenderLayer = "";
    for ($i = 0; $i < size($buffer); $i++) {
        string $word = $buffer[$i];
        if ($word == "Camera:") {
            $renderViewLastRenderCamera = $buffer[$i + 1];
            if (`objExists $renderViewLastRenderCamera`) {
                string $cameraShape[] = `listRelatives -s $renderViewLastRenderCamera`;
                if ($cameraShape[0] != "") {
                    if (`nodeType $cameraShape[0]` != "camera") {
                        $renderViewLastRenderCamera = "";
                    }
                }
            }
        }
        if ($word == "Layers:") {
            $renderViewLastRenderLayer = $buffer[$i + 1];
            if ($renderViewLastRenderLayer != "masterLayer") {
                if (`objExists $renderViewLastRenderLayer`) {
                    if (`nodeType $renderViewLastRenderLayer` != "renderLayer") {
                        $renderViewLastRenderLayer = "";
                    }
                }
            } else {
                $renderViewLastRenderLayer = "defaultRenderLayer";
            }
        }
    }
    if ($renderViewLastRenderCamera != "" && $renderViewLastRenderLayer == "") {
        $renderViewLastRenderLayer = "defaultRenderLayer";
    }
    
    string $returnValue[];
    $returnValue[0] = $renderViewLastRenderCamera;
    $returnValue[1] = $renderViewLastRenderLayer;
    
    return $returnValue;
}

global proc string rsGetRenderViewLastAovImageName(string $aovNode, int $temp, string $camera, string $renderLayer) {
    string $parts[];
    
    if ($aovNode == "Beauty") {
        $parts = redshiftGetBeautyPathParts($temp, $camera);
    } else {
        $parts = redshiftGetAovPathParts($aovNode, $temp, $camera);
    }
    
    if ($renderLayer == "defaultRenderLayer") {
        $renderLayer = "masterLayer";
    }
    
    $parts[1] = substituteAllString($parts[1], `editRenderLayerGlobals -q -currentRenderLayer`, $renderLayer);
    return redshiftBuildPathFromParts($parts, true);
}

global proc string rsGetAovLayerName(string $rsAovNode) {
    string $rsAovLayerName = "";
    
    return $rsAovLayerName;
}

global proc int rsEnableRenderPassMenuOfRenderView() {
    global string $gRenderViewLastRenderCamera;
    global string $gRenderViewLastRenderLayer;
    
    string $renderViewCurrentRenderInfo[] = `rsGetRenderViewLastRenderInfo`;
    $gRenderViewLastRenderCamera = $renderViewCurrentRenderInfo[0];
    $gRenderViewLastRenderLayer = $renderViewCurrentRenderInfo[1];
    
    int $enable = 0;
    
    if($gRenderViewLastRenderCamera != "" && $gRenderViewLastRenderLayer != "" && `renderWindowEditor -q -displayImage "renderView"` == -1) {
        if(`getAttr "defaultRenderGlobals.ren"` == "redshift") {
            string $rsAovs[] = `ls -type RedshiftAOV`;
            if ($rsAovs[0] != "") {
                $enable = 1;
            }
        }
    }
    
    return $enable;
}

global proc string rsAovToExrLayer(string $rsAov, int $index) {
    string $aovType = `getAttr ($rsAov + ".aovType")`;
    string $exrLayer;
    switch ($aovType) {
        case "Ambient Occlusion":
            $exrLayer = "*AORaw.AORaw.R";
            break;
        case "Depth":
            $exrLayer = "*Z";
            break;
        case "Diffuse Filter":
            $exrLayer = "DiffuseTint";
            break;
        case "Global Illumination":
            $exrLayer = "GI";
            break;
        case "Global Illumination Raw":
            $exrLayer = "GIRaw";
            break;
        case "ObjectID":
            $exrLayer = "*ObjectID.ObjectID.R";
            break;
        case "Puzzle Matte":
            $exrLayer = "PuzzleMatte" + $index;
            break;
        case "Reflections Filter":
            $exrLayer = "ReflectionsTint";
            break;
        case "Refractions Filter":
            $exrLayer = "RefractionsTint";
            break;
        case "Sub Surface Scatter":
            $exrLayer = "SSS";
            break;
        case "World Position":
            $exrLayer = "WorldPosition" + $index;
            break;
        default:
            $exrLayer = substituteAllString($aovType, " ", "");
            break;
    }
    return $exrLayer;
}

global proc rsSwitchAovViewingUtil() {
    global int $rsViewAovsUsingImfDisp;
    $rsViewAovsUsingImfDisp = !$rsViewAovsUsingImfDisp;
}

global proc rsLoadAov(string $aovPath, string $aovLayer) {
    string $buffer[];
    tokenize $aovPath "." $buffer;
    if ($buffer[size($buffer)-1] == "exr") {
        setAttr "defaultViewColorManager.imageColorProfile" 2;
    }
    else {
        setAttr "defaultViewColorManager.imageColorProfile" 3;
    }
    global int $rsViewAovsUsingImfDisp;
    string $editor[] = `getPanel -sty renderWindowPanel`;
    if (`rsEnableRenderPassMenuOfRenderView`) {
        if ($rsViewAovsUsingImfDisp) {
            renderWindowRenderPassMenuCallback $aovPath $aovLayer;
        } else {
            setExrLayerOverride $aovLayer;
            renderWindowEditor -e -displayImage -1 $editor[0];
            renderWindowRefreshLayout $editor[0];
            string $renderViewPCA = `renderWindowEditor -q -pca $editor[0]`;
            string $bufferLine[];
            tokenize $renderViewPCA "\\n" $bufferLine;
            string $bufferWord[];
            int $numWord = `tokenize $bufferLine[1] " " $bufferWord`;
            for ($i = 0; $i < $numWord; $i++) {
                if ($bufferWord[$i] == "Aov:") {
                    $bufferWord[$i] = "";
                    $bufferWord[$i + 1] = "";
                }
            }
            $bufferWord = stringArrayRemove({""}, $bufferWord);
            $bufferLine[1] = "";
            for ($word in $bufferWord) {
                if (endString($word, 1) == ":") {
                    $bufferLine[1] = $bufferLine[1] + $word + " ";
                } else {
                    $bufferLine[1] = $bufferLine[1] + $word + "        ";
                }
            }
            $bufferLine[1] = $bufferLine[1] + ("Aov: " + $aovLayer + "        ");
            
            renderWindowEditor -e -loadImage $aovPath $editor[0];
            renderWindowEditor -e -pca `stringArrayToString $bufferLine "\\n"` $editor[0];
            setExrLayerOverride "";
        }
    } else {
        if (`renderWindowEditor -q -displayImage "renderView"` != -1) {
            error "Please scroll to the leftmost image to enable this function.";
        } else {
            error "Please at least render on frame (Not IPR).";
        }
        
    }
}

global proc rsAddItemsToRenderPassMenuOfRenderView() {
    
    global string $gRenderViewLastRenderCamera;
    global string $gRenderViewLastRenderLayer;
    
    global int $rsViewAovsUsingImfDisp;
    
        string $renderDiagnosticFile = `rsGetRenderViewLastAovImageName "Beauty" 1 $gRenderViewLastRenderCamera $gRenderViewLastRenderLayer`;
        string $diagnosticLabel = "Beauty";
        menuItem -label "Beauty"
                    -command ("rsLoadAov \\"" + encodeString($renderDiagnosticFile) + "\\" \\"" +  $diagnosticLabel + "\\"");
        
        string $rsAovs[] = `ls -type RedshiftAOV`;
        int $worldPositionAovCount = 0;
        int $puzzleMatteAovCount = 0;
        for ($rsAov in $rsAovs) {
            if (`getAttr ($rsAov + ".enabled")`) {
                $renderDiagnosticFile = `rsGetRenderViewLastAovImageName $rsAov 1 $gRenderViewLastRenderCamera $gRenderViewLastRenderLayer`;
                $diagnosticLabel = "";
                
                string $rsAovType = `getAttr ($rsAov + ".aovType")`;
                if ($rsAovType == "World Position") {
                    $diagnosticLabel = `rsAovToExrLayer $rsAov $worldPositionAovCount`;
                    $worldPositionAovCount++;
                } else if ($rsAovType == "Puzzle Matte") {
                    $diagnosticLabel = `rsAovToExrLayer $rsAov $puzzleMatteAovCount`;
                    $puzzleMatteAovCount++;
                } else {
                    $diagnosticLabel = `rsAovToExrLayer $rsAov 0`;
                }
                
                menuItem -label $rsAov
                    -command ("rsLoadAov \\"" + encodeString($renderDiagnosticFile) + "\\" \\"" +  $diagnosticLabel + "\\"");
            }
        }
}

'''

import os.path as osp
import subprocess

def showWin(*args):
    pc.rsRender(showFeedbackDisplay=True)
    
def openFolder(*args):
    tempPath = osp.dirname(pc.renderSettings(gin=True, fpt=True)[0])
    if not osp.exists(tempPath):
        tempPath = osp.dirname(tempPath)
    subprocess.call('explorer '+ tempPath.replace('/', '\\'))
    

def aovUI():
    pc.mel.eval(switchScript)
    cmds.button('com_iceanimations_render_output',
                w=85, h=25, label='Output Folder',
                c=openFolder, p='renderViewToolbar')
    if pc.mel.currentRenderer().lower() == "redshift":
        cmds.button('com_iceanimations_redshift_aovs',
                     w = 75, h = 25, label = 'Feedback',
                     c = showWin, p = 'renderViewToolbar')
        
        cmds.menu('com_iceanimations_redshift_aovs',
                        label = '    AOV    ',
                        )
        
        pc.mel.eval('rsAddItemsToRenderPassMenuOfRenderView()')

aovUI()