'''main module for errorNodes package'''
from .error_nodes import *

__all__ = ['main', 'main_gui']


def _select_print():
    '''select all nodes in the scene and print their output'''
    nodes = get_error_nodes(False)
    select_error_nodes(nodes)
    for path in get_error_paths(nodes):
        print path
    return nodes


def main():
    '''main function'''
    return _select_print()


def main_gui():
    '''call main_gui'''
    pass

if __name__ == "__main__":
    main()
