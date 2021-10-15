//Prompt the user for a new folder location
var newLocation = Folder.selectDialog("Select a render destination...");

//Set active RQItems to render to the new location
if (newLocation) { //boolean to see if the user cancelled
    for (i = 1; i <= app.project.renderQueue.numItems; ++i) {
        var curItem = app.project.renderQueue.item(i);

        var queued = curItem.status == RQItemStatus.QUEUED;
        var needsop = curItem.status == RQItemStatus.NEEDS_OUTPUT;
        if (queued || needsop) {
            for (j = 1; j <= curItem.numOutputModules; ++j) {
                var curOM = curItem.outputModule(j); 
                var oldLocation = curOM.file;
                var folder = Folder( newLocation.toString() + "/" + curItem.comp.name );
                folder.create();
                fname = queued ? oldLocation.name : curItem.comp.name;
                curOM.file = new File(folder.toString() +  "/" + fname );
                if (needsop) { 
                    curOM.applyTemplate("JPEG Sequence"); 
                }
                alert(curOM.file.fsName);
            }
        }
    }
}
