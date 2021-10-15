
    

SETLOCAL
if "%COMPUTERNAME"=="\\NAS" (set res=1)
if "%COMPUTERNAME"=="\\NASX" (set res=1)
if "%COMPUTERNAME"=="\\NASX2" (set res=1)
if "%COMPUTERNAME"=="\\VNASX" (set res=1)
if DEFINED res (
	echo not doing anything here %1
	echo ================================================================
	GOTO :end)
echo. >> d:\deploy_user_setup.log
echo ================================================================ >> d:\deploy_user_setup.log
date /t >> d:\deploy_user_setup.log
time /t >> d:\deploy_user_setup.log
echo. >> d:\deploy_user_setup.log
echo Copying userSetup to various versions of maya >> d:\deploy_user_setup.log
for %%v in ( 2011 2012 2013 2014 2015 ) DO (
    del /F "c:/Program Files/Autodesk/Maya%%v/scripts/startup/userSetup.mel"
    del /F "c:/Program Files/Autodesk/Maya%%v/scripts/startup/iceSetup.mel"
    mklink "c:/Program Files/Autodesk/Maya%%v/scripts/startup/userSetup.mel" "R:\Pipe_Repo\Users\Hussain\utilities\loader\client\userSetup.mel"
)
rmdir /q /s "c:/ProgramData/Microsoft/Windows/Start Menu/Programs/ICE"
rmdir /q /s "c:/Program Files/ICE"
rem    mkdir "c:/Program Files/ICE"
rem    xcopy /y /s /e "R:\Pipe_Repo\Users\Qurban\applications" "c:/Program Files/ICE"
rmdir /q /s "c:/Program Files/ICE/src"
echo Adding ICE Menu to Windows Start Menu >> d:\deploy_user_setup.log
mklink /D "c:/ProgramData/Microsoft/Windows/Start Menu/Programs/ICE" "R:/Pipe_Repo/Users/Qurban/applications"
echo ================================================================ >> d:\deploy_user_setup.log
echo ================================================================
GOTO :end

:end
echo DONE
