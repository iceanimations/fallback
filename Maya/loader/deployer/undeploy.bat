@echo off
set _cmd=net view /all
cd c:\
FOR /F %%G IN ('%_cmd% ^|findstr "\\"') DO ( 
    echo %%G
    for %%k in ( 2011 2012 2013 ) DO (
        pushd "%%G\c$\Program Files\Autodesk\Maya%%k\scripts\startup" 
        del userSetup.mel
        popd
    )
)
