@echo off
set _cmd=net view /all
FOR /F %%Y IN ('%_cmd% ^|findstr "\\"') DO CALL :copy %%Y
::FOR %%Y IN (\\NASX \\NAS \\ice-087 \\ice-142 \\ice-087 \\ice-089 \\ice-088) DO CALL :copy %%Y
GOTO :end
:copy
    
    echo %1
    SETLOCAL
    if "%1"=="\\NAS" (set res=1)
    if "%1"=="\\NASX" (set res=1)
    if "%1"=="\\NASX2" (set res=1)
    if "%1"=="\\VNASX" (set res=1)
    if DEFINED res (
        echo not doing anything here %1
        echo ================================================================
        GOTO :eof
    )
    for %%v in ( 2011 2012 2013 ) DO (
        rm -f "%1/c$/Program Files/Autodesk/Maya%%v/scripts/startup/userSetup.mel"
        mklink "%1/c$/Program Files/Autodesk/Maya%%v/scripts/startup/iceSetup.mel" "R:\Pipe_Repo\Users\Hussain\utilities\loader\client\userSetup.mel"
    )
    rmdir /q /s "%1/c$/ProgramData/Microsoft/Windows/Start Menu/Programs/ICE"
    rmdir /q /s "%1/c$/Program Files/ICE"
    rem    mkdir "%1/c$/Program Files/ICE"
    rem    xcopy /y /s /e "R:\Pipe_Repo\Users\Qurban\applications" "%1/c$/Program Files/ICE"
    rmdir /q /s "%1/c$/Program Files/ICE/src"
    mklink /D "%1/c$/ProgramData/Microsoft/Windows/Start Menu/Programs/ICE" "R:/Pipe_Repo/Users/Qurban/applications"
    echo ================================================================
    GOTO :eof

:end
echo DONE
