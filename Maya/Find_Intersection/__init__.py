import IntFinder
reload(IntFinder)
import os.path as osp
from PyQt4 import uic


IntFinder.intFind(__path__[0], *uic.loadUiType("%s\ui\ui.ui" %__path__[0]))