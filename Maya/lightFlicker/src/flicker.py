# Date: Tue 17/09/2013
# Author : Hussain Parsaiyan (hussain.parsaiyan@iceanimations.com)

__all__ = ["addFlicker"]

import pymel.core as pc

def delAttr(o, at):
    if at in pc.listAttr(o):
        
        # pc.select(rel)
        return pc.Mel.eval('deleteAttr("%s.%s")'%(o, at))
        
def addAttr(o, nn, ln, sn, dv = 1,
            keyable = True, at = "double",
            min = 0.0001, max = 1000):
    if not pc.hasAttr(o, ln):
        return pc.addAttr(o, nn = nn,
                          ln = ln, sn = sn,
                          keyable = keyable, at = at,
                          min = min, max = max, dv = dv)

def addFlicker():
    for sl in list(pc.ls(sl = True)):
        for rel in pc.listRelatives(sl) + [sl]:
            if pc.nodeType(rel) == "pointLight":
                # [delAttr(*args) for args in [(rel, "flickerVariation"),
                #                              (sl, "flickerTyVariation"),
                #                              (sl, "flickerTyRange")]]
                    
                [addAttr(*args) for args in [(rel,"Flicker Variation",
                                              "flickerVariation", "fvar", 200.0),
                                             
                                             (rel, "Flicker Variation Range",
                                              "flickerVariationRange", "fvarR",
                                              ((1.15 - 0.8)/0.8 *
                                               float(rel.aiRadius.get()))),
                                             
                                             (sl, "Flicker ty Variation Frequency",
                                              "flickerTyVariation", "ftyVar", 200.0),
                                             
                                             (sl, "Flicker ty Variation Distance",
                                              "flickerTyRange", "ftyVarDis", 1.0)]]
                
                # flicker scale
                fScale = ((1.15 - 0.8)/0.8 * float(rel.aiRadius.get()))

                radExpr = ('float $fvar = {rel}.fvar;\n'+
                           'float $fvarR = {rel}.fvarR;\n'+
                           '{rel}.aiRadius = ((sin($fvar/(200) * '+
                           'time * 2 * abs(noise(time * '+
                           '$fvar/(200)))) +1)/2) * $fvarR '+
                           '+ {initRad}').format(rel = rel,
                                                 initRad = 0.1
                                                 if fScale == 0 else float(rel.aiRadius.get()))
            
                tyExpr = ("float $varTy = {sl}.ftyVarDis;\n" +
                          "float $varFreq = {sl}.ftyVar;\n" +
                          "{sl}.translateY = {initPos} + sin(time*$varFreq/200)" +
                          "*$varTy;\n").format(sl = sl,
                                            initPos = sl.translateY.get())
                # print tyExpr

                if filter(lambda expr: pc.nodeType(expr) == "expression" , rel.aiRadius.listConnections()):

                    filter(lambda expr: pc.nodeType(expr) == "expression" , rel.aiRadius.listConnections())[0].setExpression(radExpr)

                else:
                    pc.expression(o = rel, s = (radExpr),
                                  n = rel + "Expr")


                if filter(lambda expr: pc.nodeType(expr) == "expression" , sl.translateY.listConnections()):

                    filter(lambda expr: pc.nodeType(expr) == "expression" , sl.translateY.listConnections())[0].setExpression(tyExpr)

                else:

                    pc.expression(o = sl,
                                  s = (tyExpr),
                                  n = sl + "Expr")
