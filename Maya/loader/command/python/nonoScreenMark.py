import pymel.core as pc

def addAttrToFileNode():
    try:
        node = pc.ls(sl=True, type='file')[0]
    except IndexError:
        pc.warning('File node not found in the selection')
        return
        
    if not node.hasAttr('ns'):
        pc.addAttr(node, sn='ns', ln='nanoScreen', dt='string', hidden=True)
        pc.inViewMessage(msg='Marked successfully', fade=True, pos='midCenter')
    else:
        pc.inViewMessage(msg='Already marked', fade=True, pos='midCenter')