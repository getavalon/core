:: Task API for Maya
:: Create and launch from Maya working directory
::
:: This file is called whenever a user launches Maya
::
:: Arguments:
:: 	 %1: Name of task, e.g. modeling, animation
::
:: Example:
::   $ p999_Meindbender_Sync
::   $ Fiona
::   $ maya modeling

@echo off

:: if user doesn't have app installed
if Not exist "c:\program files\autodesk\maya2016\bin\maya.exe" goto :missing_app

:: if user forgot to set project or asset
if "%MINDBENDER_PROJECTPATH%"=="" goto :missing_set_project
if "%MINDBENDER_ASSET%"=="" goto :missing_set_asset

:: If user forgets to include task with "maya"..
if "%1"=="" goto :missing_task

if not exist "%1" goto :missing_taskfolder

set MINDBENDER_WORKDIR=%CD%\%1\%USERNAME%\maya
if Not exist %MINDBENDER_WORKDIR% (
	echo Creating folder for task "%1"..

	mkdir %MINDBENDER_WORKDIR%\scenes
	mkdir %MINDBENDER_WORKDIR%\data
    mkdir %MINDBENDER_WORKDIR%\renderData\shaders
	mkdir %MINDBENDER_WORKDIR%\images
	rem etc..

    copy %MINDBENDER_CORE%\res\workspace.mel %MINDBENDER_WORKDIR% >NUL
)

:: userSetup.py files
set PYTHONPATH=%PYBLISH_MAYA%\pyblish_maya\pythonpath;%PYTHONPATH%
set PYTHONPATH=%MINDBENDER_CORE%\mindbender\maya\pythonpath;%PYTHONPATH%

:: These cause Maya to "phone home" which occasionally causes
:: a lag or delay in the user interface. They have no side-effect.
set MAYA_DISABLE_CIP=1
set MAYA_DISABLE_CER=1

:: Launch (local) Maya
echo Launching Maya @ %MINDBENDER_WORKDIR%..
start "Maya" "c:\program files\autodesk\maya2016\bin\maya.exe" -proj %MINDBENDER_WORKDIR% %*

goto :eof

:missing_task
   	echo Which task? E.g. "maya modeling" or "maya rigging"
:missing_set_project
    echo You must set a project before Launch
    exit /B
:missing_set_asset
    echo You have a project set %MINDBENDER_PROJECTPATH%
    echo You must set a Asset before Launch
    exit /B
:missing_app
    echo You dont have the app installed on your workstation, or could be you dont have correct version
    exit /B
:missing_taskfolder
    echo ERROR: Unrecognised command "%1"
    exit /B
