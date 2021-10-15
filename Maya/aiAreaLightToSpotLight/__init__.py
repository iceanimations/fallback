import src._convert as con
reload(con)
convert = con.convert

import pymel.core as pc

defaultSpotLight = '''
global proc string defaultSpotLight(
    float $intensity,
    float $colourR,
    float $colourG,
    float $colourB,
    int   $decay,
    float $coneAngle,
    float $dropOff,
    float $penumbra,
    int   $shadows,
    float $shadowColourR,
    float $shadowColourG,
    float $shadowColourB,
    int   $shadowSamples,
    int      $interactive
)
{
    // get selected objects in case user wants interactive placement
    // light will be framed on objects
    string $selection[] = `ls -sl`;
    
    string $lightName = `shadingNode -asLight spotLight`;

    // setOptionVars(false);
        
    if (!`optionVar -exists spotLightIntensity`) {
        optionVar -floatValue spotLightIntensity 1;
    }
    if (!`optionVar -exists spotLightColor`) {
        optionVar -floatValue spotLightColor 1
            -floatValueAppend spotLightColor 1
            -floatValueAppend spotLightColor 1;
    }
    if (!`optionVar -exists spotLightDecay`) {
        optionVar -intValue spotLightDecay 0;
    }
    if (!`optionVar -exists spotLightConeAngle`) {
        optionVar -floatValue spotLightConeAngle 40.0;
    }
    if (!`optionVar -exists spotLightDropoff`) {
        optionVar -floatValue spotLightDropoff 0;
    }
    if (!`optionVar -exists spotLightPenumbra`) {
        optionVar -floatValue spotLightPenumbra 0;
    }
    if (!`optionVar -exists spotLightShadows`) {
        optionVar -intValue spotLightShadows false;
    }
    if (!`optionVar -exists spotLightShadowColor`) {
        optionVar -floatValue spotLightShadowColor 0
            -floatValueAppend spotLightShadowColor 0
            -floatValueAppend spotLightShadowColor 0;
    }
    if (!`optionVar -exists spotLightInteractivePlacement`) {
        optionVar -intValue spotLightInteractivePlacement 0;
    }

    string $cmd = ("setAttr " + $lightName + ".intensity " + `optionVar -query spotLightIntensity`);
    eval $cmd;
    
    float $rgb[3] = `optionVar -query spotLightColor`;
    $cmd = ("setAttr " + $lightName + ".colorR " + $rgb[0]);
    eval $cmd;
    $cmd = ("setAttr " + $lightName + ".colorG " + $rgb[1]);
    eval $cmd;
    $cmd = ("setAttr " + $lightName + ".colorB " + $rgb[2]);
    eval $cmd;

    // cant do exclusive, not in spotLight command!!!!!

    $cmd = ("setAttr " + $lightName + ".decayRate " + `optionVar -query spotLightDecay`);
    eval $cmd;

    $cmd = ("setAttr " + $lightName + ".coneAngle " + `optionVar -query spotLightConeAngle`);
    eval $cmd;

    $cmd = ("setAttr " + $lightName + ".dropoff " + `optionVar -query spotLightDropoff`);
    eval $cmd;

    $cmd = ("setAttr " + $lightName + ".penumbraAngle " + `optionVar -query spotLightPenumbra`);
    eval $cmd;

    $cmd = ("setAttr " + $lightName + ".useDepthMapShadows " + `optionVar -query spotLightShadows`);
    eval $cmd;

    $rgb = `optionVar -query spotLightShadowColor`;
    $cmd = ("setAttr " + $lightName + ".shadColorR " + $rgb[0]);
    eval $cmd;
    $cmd = ("setAttr " + $lightName + ".shadColorG " + $rgb[1]);
    eval $cmd;
    $cmd = ("setAttr " + $lightName + ".shadColorB " + $rgb[2]);
    eval $cmd;

    select -r $lightName;

    objectMoveCommand;

    if ($interactive){
        string $panel = `getPanel -withFocus`;
        if (`getPanel -typeOf $panel` == "modelPanel"){
            select -replace $lightName;
            lookThroughSelected 0 $panel;
            if (`size $selection`){
                select -replace $selection;
                fitPanel -selected;
            } else {
                fitPanel -all;
            }

        } else {
            warning((uiRes("m_defaultSpotLight.kNotAModelingPanel")));
        }
    }
    return $lightName;
}
'''

pc.mel.eval(defaultSpotLight)