import pymel.core as pc

class PostfixHierarchyUI(object):
    winName = 'PostfixHierarchyUI'

    def __init__(self):

        if pc.window(self.winName, exists=True):
            pc.deleteUI(self.winName)

        with pc.window(self.winName) as self.win:
            with pc.columnLayout(adj=True):
                self.hierBox = pc.checkBox('Select by Hierarchy', value=True)
                with pc.rowLayout(nc=2):
                    with pc.optionMenu(cc=self.changeOption) as self.postfixOption:
                        pc.menuItem(label='low')
                        pc.menuItem(label='high')
                        pc.menuItem(label='custom')
                    self.customText = pc.textField(text='')

                self.doButton = pc.button('Apply Postfix', c=self.do)
        self.customText.setEnable(False)

    def show(self):
        self.win.showWindow()

    def do(self, *args):
        postfix = self.postfixOption.getValue()
        custom_postfix = self.customText.getText().strip().strip('_')
        if postfix == 'custom':
            postfix = custom_postfix
        rep = list(replaceable_words)
        rep.append(custom_postfix)
        postfixHierarchy(word=postfix, hier=self.hierBox.getValue(),
                replaceable_words=rep)

    def changeOption(self, *args):
        if self.postfixOption.getValue() == 'custom':
            self.customText.setEnable(True)
        else:
            self.customText.setEnable(False)


replaceable_words = ( 'high', 'low' )
def postfixHierarchy(word='low', sep='_', hier=False,
        replaceable_words=replaceable_words):
    for node in pc.ls(sl=1, dag=hier, type='transform'):
        word.strip()
        word.replace(' ', '_')
        word.strip('_')
        name = node.name()
        parents = name.split('|')
        splits = parents[-1].split(sep)
        if len(splits) >= 2:
            last_word = splits[-1]
            if replaceable_words is None or last_word in replaceable_words:
                splits.pop()
            parents[-1] = '_'.join(splits)
            name = '|'.join(parents)
        newname = name
        if word:
            newname = name + sep + word
        node.rename(newname)

if __name__ == "__main__":
    PostfixHierarchyUI()
