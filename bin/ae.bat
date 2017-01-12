:: Task API for After Effects or AE
:: Create and launch from AE working directory
::
:: This file is called whenever a user launches AE
::
:: Arguments:
::   %1: Name of task, e.g. comp, roto
::
:: Example:
::   $ p999_Meindbender_Sync
::   $ sh010
::   $ ae comp

@echo off

:: if user doesn't have app installed
if Not exist "C:\Program Files\Adobe\Adobe After Effects CC 2015.3\Support Files\AfterFX.exe" goto :missing_app

:: if user forgot to set project or asset
if "%PROJECTDIR%"=="0" goto :missing_set_project

if "%ASSET%"=="0" goto :missing_set_asset

:: If user forgets to include task with "ae"..
if "%1"=="" goto :missing_task

set WORKDIR=%cd%\work\%1\%USERNAME%\AE
if Not exist %WORKDIR% (
    echo Creating new task "%1"..

    :: Arvid, redigera gärna den här Nuke mapp strukturen
    mkdir %WORKDIR%\scenes
    mkdir %WORKDIR%\data
    mkdir %WORKDIR%\images
    rem etc..
)

:: Helper variables
set PYBLISH=m:\f03_assets\include\pyblish
set GIT=%PYBLISH%\git

:: Install pyblish environment variables
::set PYTHONPATH=%PYBLISH%\etc\ae;%PYTHONPATH%

:: Install AE-specific Pyblish environment
::set AE_PATH=%GIT%\pyblish-aftereffects\;%PYTHONPATH%

:: AE-specific plug-ins
set PYBLISHPLUGINPATH=%PYBLISH%\plugins\ae;%PYBLISHPLUGINPATH%

:: Set filepath for open script window
pushd %WORKDIR%

:: Launch (local) Nuke
echo Launching AfterFX @ %WORKDIR%..
start "AfterFX" "C:\Program Files\Adobe\Adobe After Effects CC 2015.3\Support Files\AfterFX.exe"

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
