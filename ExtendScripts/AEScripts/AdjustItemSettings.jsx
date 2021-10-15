// This script will apply the provided settings on all the items of given type in the project
// if applicable
var settings = {
    //time: 30, // in seconds
    //width:720
    //height:576
    //duration:30
    pixelAspect:1.09401709401709, // D1/DV Pal
    frameRate:25.0
};

var itemTypes = [ 'Composition', 'Footage' ];

var gui_settings = {
    pixelAspect: {
        enabled: true,
        name: 'Pixel Aspect Ratio',
        type: 'dropdownlist',
        vals : {
            0.91: 0.90909090909091,
            1: 1,
            1.5: 1.5, 
            1.09: 1.09401709401709,
            1.21: 1.21212121212121, 
            1.33: 1.33333333333333, 
            1.46: 1.45868945868946, 
            2:2
        },
        dv: 2
    },
    frameRate: {
        enabled: true,
        name: 'FPS',
        type: 'dropdownlist',
        vals: {
            24: 24.0,
            25: 25.0,
            30: 30.0,
            50: 50.0,
            60: 60.0,
            120: 120.0,
            180: 180.0,
            300: 300.0
        },
        dv: 2,
    },
};

g_debug = false;

function exceptionalSetting(item, x, val, type) {
    switch (type) {
        case 'Footage':
            source = item.useProxy ? 'proxySource' : 'mainSource';
            switch (x) {
                case 'frameRate':
                    if (!item.isStill && !item[source].isStill) {
                        item[source].conformFrameRate = val;
                        if (g_debug)
                            $.writeln("\"" + item.name + "\"." + x + " = " + val);
                    }
                    return true;
                case 'time':
                    if (item.isStill) return true;
                    break;
                case 'width':
                case 'height':
                    if ('file' in item[source]) // filesource
                        return true;
                    break;
                case 'duration':
                    return true;
            } // switch x
    } // switch type
    return false;
}

function applySettingsToItems(items, settings, itemTypes) {
    for (i=1; i<=items.length;i++) {
        item = items[i];
        type = item.typeName;
        for (var it in itemTypes) {
            itemType=itemTypes[it];
            if (type == itemType) {
                for (var x in settings) {
                    try {
                        if (!exceptionalSetting(item, x, settings[x], itemType) && x in item) {
                            item[x]=settings[x];
                            if (g_debug)
                                $.writeln('\"' + item.name + '\".' + x + ' = ' + settings[x]);
                        }
                    }
                    catch (err) {
                        $.writeln([err, item.name + '.' + x]);
                    } // try ... catch
                } // for
                break; // from itemTypes
            }
        } // for itemTypes
    } // for items
    return true;
}

function settingGroupsUI(panel) {
    panel.grps = [];
    for (var s in gui_settings ) {
        grp = panel.add('group');
        grp.check = grp.add('checkbox', undefined, gui_settings[s].name);
        grp.check.helpTip = s;
        grp.check.value = gui_settings[s].enabled;
        grp.s = s;
        grp.gs = gui_settings[s];
        panel.grps.push(grp);

        if (grp.gs.type == 'dropdownlist') {
            grp.ddl = grp.add('dropdownlist', undefined, 'value');
            for (var val in grp.gs.vals) {
                grp.ddl.add('item', val);
            }
            grp.ddl.selection = grp.gs.dv;
            grp.check.onClick = function() {
                this.parent.children[1].visible=this.value;
            };
        }

        else if (grp.gs.type == 'slider') {
            grp.stsldr = grp.add('statictext', undefined, grp.gs.dv);
            grp.sldr = grp.add('slider', undefined,
                    grp.gs.dv,
                    grp.gs.min,
                    grp.gs.max);
            grp.sldr.onChanging = function() {
                this.parent.stsldr.text=this.value;
            };
            grp.check.onClick = function() {
                this.parent.sldr.visible=this.value;
                this.parent.stsldr.visible=this.value;
            };
        }
    }
}


function doApply() {
        dlg = this.parent.parent;
        applyTo = [];
        if (dlg.compCheck.value) applyTo.push('Composition');
        if (dlg.footageCheck.value) applyTo.push('Footage');
        settings = {};
        for (var i in dlg.settingsPanel.grps) {
            grp = dlg.settingsPanel.grps[i];
            key = grp.s;
            val = 0;
            if (grp.gs.type == 'slider')
                val = grp.sldr.value;
            else if (grp.gs.type == 'dropdownlist')
                val = grp.gs.vals[grp.ddl.selection.text];
            settings[key]=val;
        }
        applySettingsToItems(app.project.items, settings, applyTo);
        dlg.close(true);
}

function applySettingsUI() {
    dlg = new Window('dialog', 'Adjust Settings for all Items', undefined, {resizeable: true});

    itemTypePanel = dlg.add('panel', undefined, 'Apply On:');
    itemTypePanel.alignChildren = 'left';
    dlg.compCheck = itemTypePanel.add('checkbox', undefined, 'Compositions');
    dlg.compCheck.value = true;
    dlg.footageCheck = itemTypePanel.add('checkbox', undefined, 'Footages');
    dlg.footageCheck.value = true;

    dlg.settingsPanel = dlg.add('panel', undefined, 'Settings');
    dlg.settingsPanel.alignChildren = 'left';
    settingGroupsUI(dlg.settingsPanel);

    btnGrp = dlg.add('group');
    applyBtn = btnGrp.add('button', undefined, 'Apply');
    cancelBtn = btnGrp.add('button', undefined, 'Cancel');
    applyBtn.onClick = doApply;

    dlg.center();
    return dlg.show();
}
applySettingsUI();

