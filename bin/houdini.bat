:: Task API for Houdini
:: Create and launch from Houdini working directory
::
:: This file is called whenever a user launches Houdini
::
:: Arguments:
::   %1: Name of task, e.g. fx, sim
::
:: Example:
::   $ p999_Meindbender_Sync
::   $ sh010
::   $ Houdini fx

@echo off

:: if user doesn't have app installed
if Not exist "C:\Program Files\Side Effects Software\Houdini 15.5.523\bin\houdinifx.exe" goto :missing_app

:: if user forgot to set project or asset
if "%PROJECTDIR%"=="0" goto :missing_set_project

if "%ASSET%"=="0" goto :missing_set_asset

:: If user forgets to include task with "houdini"..
if "%1"=="" goto :missing_task

set WORKDIR=%cd%\work\%1\%USERNAME%\houdini
if Not exist %WORKDIR% (
    echo Creating new task "%1"..

    :: Arvid, redigera gärna den här Houdini mapp strukturen
    mkdir %WORKDIR%\scenes
    mkdir %WORKDIR%\data
    mkdir %WORKDIR%\images
    rem etc..
)

:: Helper variables
set PYBLISH=m:\f03_assets\include\pyblish
set GIT=%PYBLISH%\git

:: Install Houdini-specific Pyblish environment
set "HOUDINI_PATH=%GIT%\pyblish-houdini\pyblish_houdini\houdini_path;&;%HOUDINI_PATH%"
set "HOUDINI_PATH=%PYBLISH%\etc\houdini\;&;%HOUDINI_PATH%"

:: Houdini-specific plug-ins
set PYBLISHPLUGINPATH=%PYBLISH%\plugins\nuke;%PYBLISHPLUGINPATH%

:: Set filepath for open script window
pushd %WORKDIR%

:: Launch (local) Houdini
echo Launching Houdini @ %WORKDIR% ..
start "Houdini" "C:\Program Files\Side Effects Software\Houdini 15.5.523\bin\happrentice.exe"
popd

goto :eof

:missing_task
    Echo Which task? E.g. "comp", "roto"
:missing_set_project
    Echo You must set a project before Launch
    Exit /B
:missing_set_asset
    Echo You have a project set %PROJECTDIR%
    Echo You must set a Asset before Launch
    Exit /B
:missing_app
    Echo You dont have the app installed on your workstation, or could be you dont have correct version
    Exit /B
