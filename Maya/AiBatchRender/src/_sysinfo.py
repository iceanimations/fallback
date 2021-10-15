'''
Created on Jul 28, 2014

@author: Qurban Ali
'''
import os.path as osp
import os

directory = r'\\nas\storage\.db\ai_batch_render'
    
def get_info(systm):
    global directory
    try:
        f = open(directory + systm+'.txt')
        result = eval(f.read())
        f.close()
        if (result['maya'] and result['arnold']):
            return True
        return False
    except IOError:
        return False
