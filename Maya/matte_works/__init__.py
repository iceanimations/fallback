import matteWorker
reload(matteWorker)
import os.path as osp
from PyQt4 import uic

matteWorker.matteWork(__path__[0], *uic.loadUiType("%s\ui\ui.ui" %__path__[0]))