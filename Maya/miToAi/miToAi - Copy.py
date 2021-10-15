import pymel.core as pc

def connectAttributes():
    nodes = pc.ls(sl = True)
    if not nodes:
        pc.warning("No object selected")
        return
    if len(nodes) < 2:
        pc.warning("Select two objects")
        return
    if len(nodes) > 2:
        pc.warning("More than two objects are selected, select two")
        return
    if type(nodes[0]) != pc.nt.Mia_material_x_passes or type(nodes[1]) != pc.nt.AiStandard:
        pc.warning("First node => Mi, second node => Ai. Sequence not matched")
        return
    for node in pc.listConnections(nodes[0]):
        if type(node) == pc.nt.File:
            node.outColor >> nodes[1].KsColor
        if type(node) == pc.nt.Bump2d:
            node.outNormal >> nodes[1].normalCamera
        if type(node) == pc.nt.GammaCorrect:
            node.outValue >> nodes[1].color
    pc.disconnectAttr(nodes[0].reflectivity)
    pc.disconnectAttr(nodes[0].refl_color)
    pc.disconnectAttr(nodes[0].overall_bump)
    pc.disconnectAttr(nodes[0].diffuse)