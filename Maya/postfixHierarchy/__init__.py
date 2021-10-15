from . import _postfix
reload(_postfix)

Window = _postfix.PostfixHierarchyUI
applyPostfix = _postfix.postfixHierarchy
