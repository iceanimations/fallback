'''
Created on May 14, 2016

@author: qurban.ali
'''
import nuke
import os.path as osp

def createMovie(jpgPath, outputPath, first, last):
    
    node = nuke.createNode('Read')
    write = nuke.createNode('Write')
    
    node.knob('file').setValue(jpgPath)
    node.knob('first').setValue(first)
    node.knob('last').setValue(last)
    node.knob('origfirst').setValue(first)
    node.knob('origlast').setValue(last)
    
    write.knob('file_type').setValue(7)
    write.knob('mov64_fps').setValue(25)
    #write.knob('mov64_audiofile').setValue(audioPath)
    write.knob('file').setValue(outputPath)
    nuke.execute(write, first, last, continueOnError=True)
    
if __name__ == '__main__':
    info = []
    with open(osp.join(osp.expanduser('mse_compositing'), 'info.txt')) as f:
        info[:] = eval(f.read())
    createMovie(*info)