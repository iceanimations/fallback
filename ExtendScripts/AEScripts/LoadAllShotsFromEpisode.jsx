////////////////////////////////////////////////////////////////////////
//                    Production Elements Library                     //
////////////////////////////////////////////////////////////////////////

////////////////////////
//  global constants  //
////////////////////////


var top_seq_folder  = 'SEQUENCES';
var top_sh_folder = 'SHOTS';
var animatic_folder = 'animatic';

/////////////////////////
//  utility functions  //
/////////////////////////

var elementConstructor = function (obj, folder) {
    if (!folder instanceof Folder ){
        folder = Folder(folder);
    }
    obj.folder = folder;
    obj.name = function(){
        return obj.folder.name;
    };
    obj.toString = function(){
        return obj.type + ' ( \'' + obj.folder.fullName +'\' )';
    };
};

var checkValidity = function (obj, folder, subfolder_name, regexp) {
    var _folder = null;

    if (obj.folder === undefined){
        _folder = folder;
    }
    else {
        _folder = obj.folder;
    }

    if ( _folder === null || !_folder instanceof Folder ) {
        throw new TypeError('argument should be of type Folder');
    }

    if (regexp instanceof RegExp){
        if (!regexp.exec(_folder.name)){
            return false;
        }
    }

    if (subfolder_name !== undefined) {
        if ( _folder.exists) {
            subfolder = false;
            var files = _folder.getFiles();
            for ( var i in files ){
                item = files[i];
                if (item instanceof Folder && item.name == subfolder_name)
                    subfolder = true;
            }
            if (!subfolder)
                return false;
        }
    }
    return true;
};

var getSubFolder = function (folder, subfolder_name) {
    if ( folder.exists) {
        var files = folder.getFiles();
        for ( var i in files ){
            item = files[i];
            if (item instanceof Folder && item.name == subfolder_name)
                return item;
        }
    }
};

var getChildren = function(topFolder, type) {
    var files = topFolder.getFiles();
    var sequences = [];
    for (var f in files) {
        var item = files[f];
        if ( type.isValid(item) ) {
            sequences.push( new type(item) );
        }
    }
    return sequences;
};

//////////////////////////////////
//  Production Element Objects  //
//////////////////////////////////

var Episode = function(folder) {
    this.type = 'Episode';
    elementConstructor(this, folder);
    this.getTopSequencesFolder =  function() {
        return getSubFolder(this.folder, top_seq_folder);
    };
    this.getSequences = function () {
        var topFolder = this.getTopSequencesFolder();
        return getChildren(topFolder, Sequence);
    };
    this.importAnimatic = function(rootFolder) {
        var items = app.project.items;
        if (rootFolder === undefined){
            rootFolder = app.project.rootFolder;
        }
        var epFolder = items.addFolder(this.name());
        epFolder.parentFolder = rootFolder;
        var sequences = this.getSequences();
        for (var s in sequences) {
            var seq = sequences[s];
            seq.importAnimatic(epFolder);

        }
        return epFolder;
    };
};
Episode.isValid = Episode.prototype.isValid = function(folder) {
    return checkValidity(this, folder, top_seq_folder);
};

var Sequence = function(folder) {
    this.type = 'Sequence';
    elementConstructor(this, folder);
    this.getEpisode = function() {
        if ( Episode.isValid(this.folder.parent.parent) )
            return new Episode(this.folder.parent.parent);
    };
    this.getTopShotsFolder = function() {
        return getSubFolder(this.folder, top_sh_folder);
    };
    Sequence.prototype.getShots = function () {
        var topFolder = this.getTopShotsFolder();
        return getChildren(topFolder, Shot);
    };
    this.importAnimatic = function(rootFolder) {
        var items = app.project.items;
        if (rootFolder === undefined){
            rootFolder = app.project.rootFolder;
        }
        var seqFolder = items.addFolder(this.name());
        seqFolder.parentFolder = rootFolder;
        var shots = this.getShots();
        for (var s in shots) {
            var shot = shots[s];
            shot.importAnimatic(seqFolder);
        }
        return seqFolder;
    };
};
Sequence.isValid = Sequence.prototype.isValid = function(folder) {
    return checkValidity(this, folder, top_sh_folder, Sequence.regexp);
};
Sequence.regexp = Sequence.prototype.regexp = new RegExp('^SQ\\d{3}$');

var Shot = function(folder){
    this.type = 'Sequence';
    elementConstructor(this, folder);
    this.getSequence = function() {
        if (Sequence.isValid(this.folder.parent.parent))
            return new Sequence(this.folder.parent.parent);
    };
    this.getAnimaticFolder = function() {
        return getSubFolder(this.folder, animatic_folder);
    };
    this.getAnimatic = function() {
        var animaticFolder = this.getAnimaticFolder();
        var files = animaticFolder.getFiles('*.jpg');
        if (files)
            return files[0];
    };
    this.importAnimatic = function(rootFolder) {
        var items = app.project.items;
        if (rootFolder === undefined){
            rootFolder = app.project.rootFolder;
        }
        shFolder = items.addFolder(this.name());
        shFolder.parentFolder = rootFolder;
        var animatic = this.getAnimatic();

        if (animatic) {
            var options = new ImportOptions(animatic);
            options.importAs = ImportAsType.FOOTAGE;
            options.sequence = true;
            var foot = app.project.importFile(options);
            foot.parentFolder = shFolder;
        }
        return shFolder;
    };
};
Shot.isValid = Shot.prototype.isValid = function(folder) {
    return checkValidity(this, folder, animatic_folder, Shot.regexp);
};
Shot.regexp = Shot.prototype.regexp = new RegExp('^SQ\\d{3}_SH\\d{3}$');

///////////////
//  factory  //
///////////////

var detectElement = function(folder) {
    if ( Episode.isValid(folder) )
        return new Episode(folder);
    else if ( Sequence.isValid(folder) )
        return new Sequence(folder);
    else if ( Shot.isValid(folder) )
        return new Shot(folder);
};

////////////////////////////////////////////////////////////////////////
//                  End Production Elements Library                   //
////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////
//                           main functions                           //
////////////////////////////////////////////////////////////////////////

var importEpisodeAnimatics = function(path) {
    if (path === undefined) {
        path = Folder.selectDialog('Select Episode or Sequence Location');
    }
    var elem = detectElement(path);
    if (elem ===  undefined) {
        alert();
    }
    elem.importAnimatic();
};

var path = Folder('/P/external/Al_Mansour_Season_03/Edit/Episode_001/animatics/EP001');
importEpisodeAnimatics();

