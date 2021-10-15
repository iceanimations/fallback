import pymel.core as pc
import re

def get_controls(sl=False):
    return [node.firstParent() for node in pc.ls(type='nurbsCurve', sl=sl)]

def rename_controls(removeCharPrefix=None, add_underscore_to_lr=True, controls=None):

    if controls is None:
        controls = get_controls()

    if removeCharPrefix and removeCharPrefix.endswith('_'):
        removeCharPrefix = removeCharPrefix[:-1]

    if removeCharPrefix:
        cp = re.compile(removeCharPrefix+ '_' )

    if add_underscore_to_lr:
        lr = re.compile('(_?)(r|l)([A-Z]{1})')


    for node in controls:

        locked = pc.lockNode(node, q=1)
        if locked:
            pc.lockNode(node, l=False)

        newname = unicode( node )
        sub = 0

        if removeCharPrefix:
            _newname, _sub = cp.subn('', newname )
            if _sub:
                newname = _newname
                sub += _sub

        if add_underscore_to_lr:
            _newname, _sub = lr.subn(r'_\2_\3', newname)
            if _sub:
                newname = _newname
            sub += _sub

        if sub:
            print 'renaming', node, 'to', newname
            node.rename(newname)

        if locked:
            pc.lockNode(node, l=True)

class RigRenameGUI(object):
    name = 'RigRenameGUI'

    def __init__(self):
        if pc.window(self.name, exists=True):
            pc.deleteUI(self.name)
        with pc.window(self.name, title='Rig Renamer'):
            with pc.columnLayout(adj=True):
                self.detectButton = pc.button('Detect Character Prefix',
                        c=self.detect_and_update)
                self.charPrefixField = pc.textFieldGrp(label='Char_PrefixName')
                self.doUnderscoreCheck = pc.checkBoxGrp(v1=True,
                        label='add underscore to lr    ')
                self.useSelectionCheck = pc.checkBoxGrp(v1=False,
                        label='rename selected controls only    ')
                self.doButton = pc.button('Rename', c=self.do)
        self.detect_and_update()

    def do(self, *args):
        pre = self.charPrefixField.getText()
        und = self.doUnderscoreCheck.getValue1()
        sel = self.useSelectionCheck.getValue1()
        con = get_controls(sl=sel)
        rename_controls(removeCharPrefix=pre, add_underscore_to_lr=und,
                controls=con)

    def detect_and_update(self, *args):
        self.charPrefixField.setText(str(self.detect()))

    def detect(self):
        prefix = ''
        for node in pc.ls(regex='(?i).*mainc[^|]*', type='nurbsCurve'):
            match = re.match('(?i)(.*)mainc[^|]*', unicode( node ) )
            prefix = match.group(1)
            if prefix:
                break
        return prefix


if __name__ == "__main__":
    # rename_controls(removeCharPrefix='Ch')
    RigRenameGUI()


