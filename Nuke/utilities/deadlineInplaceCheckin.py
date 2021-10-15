import site
site.addsitedir('R:/Pipe_Repo/Projects/TACTIC')
site.addsitedir('D:/my/tasks/workSpace/utilities')
site.addsitedir('D:/My/Tasks/workSpace')
import tacticCalls
import os.path as osp
import iutil

#TODO: Modify the created file object in snapshot to contain the file paths against the main file key instead of source path key

def __main__(*args):
    deadlinePlugin = args[0]
    job = deadlinePlugin.GetJob()
    
    outputDirectories = job.OutputDirectories
    outputFilenames = job.OutputFileNames
    
    project = job.JobExtraInfo0.split('=')[-1]
    episode = job.JobExtraInfo1.split('=')[-1]
    sequence = job.JobExtraInfo2.split('=')[-1]
    shot = job.JobExtraInfo3.split('=')[-1]
    layer = job.JobExtraInfo4.split('=')[-1]
    AOVs = job.JobExtraInfo5.split('=')[-1].split(',')
    if AOVs: AOVs = set([layer +'_'+ aov for aov in AOVs])
    s, e = tacticCalls.setServer()
    if not e:
        deadlinePlugin.LogInfo(str(tacticCalls.setProject(project)))
        startFrame = deadlinePlugin.GetStartFrame()
        endFrame = deadlinePlugin.GetEndFrame()
        frameRange = str(startFrame) +'-'+ str(endFrame) +'/1'
        # fullShot = '_'.join([episode, sequence, shot])
        tLayer, e = tacticCalls.addShotLayer(layer, 'E01_SQ001_SH001')
        
        if not e:
            # create snapshot here, add files inside the loop by specifying aovs as file_types
            sk = tLayer['__search_key__']
            for i in range( 0, len(outputDirectories) ):
                outputDirectory = outputDirectories[i]
                outputFilename = outputFilenames[i].replace('?', '#')
                if AOVs:
                    context = set(iutil.splitPath(outputDirectory)).intersection(AOVs)
                    if not context: context = layer +'_beauty'
                    else: context = context.pop()
                else:
                    context = layer +'_renders'
                errors = tacticCalls.checkinRenders(sk, context, osp.join(outputDirectory, outputFilename), frameRange)
                if errors:
                    deadlinePlugin.LogInfo(str(errors))
        else:
            deadlinePlugin.LogInfo('ERROR: Could not add new layer to TACTIC (%s): %s'%(layer, str(e)))
            
    else:
        deadlinePlugin.LogInfo('ERROR: Could not get TACTIC server: %s'%str(e))