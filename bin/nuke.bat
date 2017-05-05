:: Task API for Nuke
:: Create and launch from Nuke working directory
::
:: This file is called whenever a user launches Nuke
::
:: Arguments:
::   %1: Name of task, e.g. comp, roto
::
:: Example:
::   $ p999_Meindbender_Sync
::   $ sh010
::   $ nuke comp

@echo off

:: if user doesn't have app installed
:: if Not exist "C:\Program Files\The Foundry\NUKE\Nuke10.0v2\Nuke10.0.exe" goto :missing_app

:: if user forgot to set project or asset
if "%MINDBENDER_PROJECTPATH%"=="" goto :missing_set_project
if "%MINDBENDER_ASSET%"=="" goto :missing_set_asset

:: If user forgets to include task with "maya"..
if "%1"=="" goto :missing_task

if not exist "%1" goto :missing_taskfolder

set MINDBENDER_WORKDIR=%cd%\%1\nuke
if Not exist %MINDBENDER_WORKDIR% (
    echo Creating new task "%1"..

    :: Arvid, redigera gärna den här Nuke mapp strukturen
    mkdir %MINDBENDER_WORKDIR%\nk
    mkdir %MINDBENDER_WORKDIR%\scripts
    mkdir %MINDBENDER_WORKDIR%\cache
    mkdir %MINDBENDER_WORKDIR%\render
    rem etc..
)

:: Initialisation files
set NUKE_PATH=%MINDBENDER_CORE%\mindbender\nuke\nuke_path;%NUKE_PATH%
set PYBLISHPLUGINPATH=%MINDBENDER_CORE%\mindbender\plugins\nuke;%PYBLISHPLUGINPATH%

:: Set filepath for open script window
pushd %MINDBENDER_WORKDIR%\nk

:: Launch (local) Nuke
echo Launching NukeX @ %MINDBENDER_WORKDIR%..
start "NukeX" "C:\Program Files\The Foundry\NUKE\Nuke10.0v2\Nuke10.0" --nukex

popd
goto :eof

:missing_task
    Echo Which task? E.g. "comp", "roto"
:missing_set_project
    Echo You must set a project before Launch
    Exit /B
:missing_set_asset
    Echo You have a project set %MINDBENDER_PROJECTPATH%
    Echo You must set a Asset before Launch
    Exit /B
:missing_app
    Echo You dont have the app installed on your workstation, or could be you dont have correct version
    Exit /B
:missing_taskfolder
    echo ERROR: Unrecognised command "%1"
    exit /B
