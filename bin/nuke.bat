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
if "%PROJECTDIR%"=="0" goto :missing_set_project

if "%ASSET%"=="0" goto :missing_set_asset

:: If user forgets to include task with "nuke"..
if "%1"=="" goto :missing_task

set WORKDIR=%cd%\work\%1\%USERNAME%\nuke
if Not exist %WORKDIR% (
    echo Creating new task "%1"..

    :: Arvid, redigera gärna den här Nuke mapp strukturen
    mkdir %WORKDIR%\nk
    mkdir %WORKDIR%\scripts
    mkdir %WORKDIR%\cache
    mkdir %WORKDIR%\render
    rem etc..
)

:: Helper variables
set PYBLISH=m:\f03_assets\include\pyblish
set GIT=%PYBLISH%\git

:: Install Nuke-specific Pyblish environment
set NUKE_PATH=%PYBLISH%\etc\nuke;%NUKE_PATH%

:: Nuke-specific plug-ins
set PYBLISHPLUGINPATH=%PYBLISH%\plugins\nuke;%PYBLISHPLUGINPATH%

:: Set filepath for open script window
pushd %WORKDIR%\nk

:: Launch (local) Nuke
echo Launching NukeX @ %WORKDIR%..
start "NukeX" "C:\Program Files\The Foundry\NUKE\Nuke10.0v2\Nuke10.0" --nukex

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
