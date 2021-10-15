'''

'''
import nuke
import nukescripts


__all__ = ['get_error_paths', 'get_error_nodes', 'select_error_nodes']


def get_error_nodes(use_selected=True):
    '''return a list of read nodes that has error

    @type useSelected bool

    @return list
    '''
    get_nodes = nukescripts.allNodes
    if use_selected:
        get_nodes = nuke.selectedNodes()

    errorNodes = []
    for node in get_nodes():
        if node.Class() == 'Read' and node.error():
            errorNodes.append(node)

    return errorNodes


def get_error_paths(nodes=None, use_selected=True):
    ''' Return a list of paths collected from read nodes

    @param nodes list
    @param useSelected bool

    @return list
    '''
    if nodes is None:
        nodes = get_error_nodes(use_selected)

    paths = []
    for node in nodes:
        file_value = node.knob('file').getValue()
        if file_value:
            paths.append(file_value)
    return paths


def select_error_nodes(nodes=None, use_selected=True):
    ''' Select All Error Nodes

    @param nodes list
    @param useSelected bool
    '''
    if nodes is None:
        nodes = get_error_nodes(use_selected)

    nukescripts.clear_selection_recursive()
    for node in nodes:
        node.setSelected(True)
