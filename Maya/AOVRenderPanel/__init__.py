import pymel.core as pc
import os
op = os.path
SPRT_FOR = map(str,[2013,
                    2014,
                    2015])
VER = pc.about(v = True)

for ver in SPRT_FOR:
    if ver in VER:
        renderWindowPanel = op.join(op.dirname(__file__ ),
                                    'renderWindowPanel'+ '_' + ver + '.mel')
        arnoldmenu_file = __file__.replace('\\', '/')
        pc.mel.eval('global string $ice_arnold_aov_menu_gen = "%s";'
                    %(op.dirname(arnoldmenu_file).replace('\\', '/') + '/redshiftmenu.py'))
        pc.mel.eval('source "%s";'%(renderWindowPanel.replace('\\', '/')))