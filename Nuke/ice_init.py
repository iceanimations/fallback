import os
import sys
import nuke

__dir__ = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, __dir__)
sys.path.append('r:/Python_Scripts/Nuke')
sys.path.append('r:/Python_Scripts/plugins')
sys.path.append('r:/Python_Scripts/plugins/utilities')

if nuke.NUKE_VERSION_MAJOR < 9:
    os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(
            ['PyQt4', 'PyQt5', 'PySide', 'PySide2'])
    sys.path.append('r:/Python_Scripts/maya2014/PyQt')


import startup
startup.setupNuke()
