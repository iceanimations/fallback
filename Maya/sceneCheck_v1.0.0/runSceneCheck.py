# Embedded file name: R:\Python_Scripts\plugins\sceneCheck_v1.0.0\runSceneCheck.py
import os
import sys
path = __file__
path, file = os.path.split(path)
if path not in sys.path:
    sys.path.insert(0, path)
ui_path = '%s/src/ui' % path
if ui_path not in sys.path:
    sys.path.insert(0, ui_path)
modules_path = '%s/modules' % path
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)
import site
site.addsitedir('R:\\Python_Scripts\\plugins\\utilities')
from uiContainer import sip
sys.modules['sip'] = sip
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sceneCheckUI
reload(sceneCheckUI)
sCheckWindow = sceneCheckUI.createSceneCheckWin()
sCheckWindow.show()